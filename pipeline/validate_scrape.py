"""Validate a scraped corpus CSV before building embeddings/ChromaDB.

Runs two kinds of checks on the output of scrape_guides.py:

  FAIL — schema/integrity violations that break the pipeline contract
         (see PIPELINE_PLAN.md, "Integration Contract"): wrong columns,
         non-unique/non-sequential local_id, empty text, malformed URLs,
         parent_ids not in url_list.csv.
  WARN — quality signals worth a human look: guides with no rows, large
         row-count drops versus the previous corpus, very short texts.

Exits non-zero if any FAIL check trips.

Usage:
    pixi run python pipeline/validate_scrape.py
    pixi run python pipeline/validate_scrape.py --input /path/to.csv --no-baseline
"""

import argparse
import json
import sys
from urllib.parse import urlparse

from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from libbot_pkg.config import load_settings 

import pandas as pd

# ---------- Defaults ----------
INPUT_CSV = "/dsl/libbot/data/text_full_libguide_new.csv"
BASELINE_CSV = "/dsl/libbot/data/text_full_libguide.csv"
URL_LIST_PATH = "/dsl/libbot/data/url_list.csv"
MIN_TEXT_CHARS = 20      # texts shorter than this are flagged
ROW_DROP_WARN = 0.5      # warn if a guide lost >50% of its baseline rows
# ------------------------------

EXPECTED_COLUMNS = ["local_id", "parent_id", "text", "libguide_title",
                    "libguide_url", "chunk_title", "chunk_url", "external_url",
                    "authors"]
AUTHOR_KEYS = {"name", "profile_url", "email"}
AUTHOR_COVERAGE_FAIL = 0.5   # fail if fewer guides than this have authors

failures = []
warnings = []


def fail(msg: str):
    failures.append(msg)
    print(f"  FAIL: {msg}")


def warn(msg: str):
    warnings.append(msg)
    print(f"  WARN: {msg}")


def ok(msg: str):
    print(f"  ok:   {msg}")


def is_valid_url(value: str) -> bool:
    parsed = urlparse(str(value))
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def check_schema(df: pd.DataFrame):
    print("\n== Schema ==")
    if list(df.columns) != EXPECTED_COLUMNS:
        fail(f"Columns are {list(df.columns)}, expected {EXPECTED_COLUMNS}")
        return
    ok(f"All {len(EXPECTED_COLUMNS)} expected columns present, in order")

    if not df["local_id"].is_unique:
        fail("local_id is not unique")
    elif not (df["local_id"] == range(1, len(df) + 1)).all():
        fail("local_id is not sequential 1..N")
    else:
        ok(f"local_id sequential 1..{len(df)}")

    for col in ("local_id", "parent_id"):
        if not pd.api.types.is_integer_dtype(df[col]):
            fail(f"{col} is not an integer column (dtype={df[col].dtype})")


def check_content(df: pd.DataFrame):
    print("\n== Content ==")
    for col in ("text", "libguide_title", "libguide_url", "chunk_title"):
        empty = df[col].isna() | (df[col].astype(str).str.strip() == "")
        if empty.any():
            fail(f"{int(empty.sum())} rows have empty {col}")
        else:
            ok(f"No empty {col}")

    for col in ("libguide_url", "chunk_url", "external_url"):
        present = df[col].dropna()
        present = present[present.astype(str).str.strip() != ""]
        bad = present[~present.map(is_valid_url)]
        if len(bad):
            fail(f"{len(bad)} malformed URLs in {col}, e.g. {bad.iloc[0]!r}")
        else:
            ok(f"All {len(present)} non-empty {col} values are valid URLs")

    lengths = df["text"].astype(str).str.len()
    short = int((lengths < MIN_TEXT_CHARS).sum())
    print(f"  text length: min={lengths.min()} median={int(lengths.median())} "
          f"max={lengths.max()}")
    if short:
        warn(f"{short} rows have text shorter than {MIN_TEXT_CHARS} chars")

    dup_pct = 100 * (1 - df["text"].nunique() / len(df))
    print(f"  duplicate text rate: {dup_pct:.0f}% "
          "(the retriever expects and dedups heavy duplication)")


def check_authors(df: pd.DataFrame):
    print("\n== Authors ==")
    if "authors" not in df.columns:
        fail("authors column is missing")
        return

    def parse(value):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else None
        except (TypeError, ValueError):
            return None

    per_guide = df.groupby("parent_id")["authors"].first().map(parse)
    bad = per_guide[per_guide.isna()]
    if len(bad):
        fail(f"{len(bad)} guides have an unparsable authors field "
             f"(parent_ids {list(bad.index[:5])})")
        return
    ok("authors parses as a JSON list for every guide")

    bad_entries = per_guide[per_guide.map(
        lambda entries: any(not AUTHOR_KEYS <= set(e) for e in entries))]
    if len(bad_entries):
        fail(f"{len(bad_entries)} guides have author entries missing "
             f"name/profile_url/email keys (parent_ids {list(bad_entries.index[:5])})")
    else:
        ok("Every author entry has name, profile_url and email")

    has_authors = per_guide.map(len) > 0
    coverage = has_authors.mean()
    print(f"  guides with at least one author: {int(has_authors.sum())}"
          f"/{len(per_guide)} ({coverage:.0%})")
    unresolved = per_guide.map(
        lambda entries: sum(1 for e in entries if not e.get("name")))
    if unresolved.sum():
        warn(f"{int(unresolved.sum())} author entries have an email but no "
             "resolved name (directory API lookup failed)")
    if coverage < AUTHOR_COVERAGE_FAIL:
        fail(f"Only {coverage:.0%} of guides have authors "
             f"(expected at least {AUTHOR_COVERAGE_FAIL:.0%}) — extraction looks broken")
    elif not has_authors.all():
        missing = per_guide[~has_authors]
        warn(f"{len(missing)} guides have no authors (parent_ids "
             f"{list(missing.index[:15])})")


def check_coverage(df: pd.DataFrame, url_list_path: str):
    print("\n== Guide coverage ==")
    urls = pd.read_csv(url_list_path)
    unknown = set(df["parent_id"]) - set(urls["id"])
    if unknown:
        fail(f"{len(unknown)} parent_ids not present in url_list.csv: "
             f"{sorted(unknown)[:10]}")
    else:
        ok("Every parent_id maps to an id in url_list.csv")

    missing = urls[~urls["id"].isin(df["parent_id"])]
    print(f"  guides with content: {df['parent_id'].nunique()}/{len(urls)}")
    if len(missing):
        warn(f"{len(missing)} guides from url_list.csv produced no rows:")
        for row in missing.itertuples(index=False):
            print(f"        id={row.id} {row.url}")

    per_guide = df.groupby("parent_id").size()
    print(f"  rows per guide: min={per_guide.min()} median={int(per_guide.median())} "
          f"max={per_guide.max()}")


def check_against_baseline(df: pd.DataFrame, baseline_path: str):
    print(f"\n== Baseline comparison ({baseline_path}) ==")
    try:
        old = pd.read_csv(baseline_path, encoding="utf-8")
    except FileNotFoundError:
        warn("Baseline CSV not found; skipping comparison")
        return

    print(f"  rows: baseline={len(old)} new={len(df)}")
    print(f"  guides (by libguide_url): baseline={old['libguide_url'].nunique()} "
          f"new={df['libguide_url'].nunique()}")

    overlap = df["chunk_title"].isin(set(old["chunk_title"])).mean()
    print(f"  new rows whose chunk_title existed in baseline: {overlap:.0%} "
          "(low values can simply mean guides were edited)")

    shared = set(old["libguide_url"]) & set(df["libguide_url"])
    old_counts = old[old["libguide_url"].isin(shared)].groupby("libguide_url").size()
    new_counts = df[df["libguide_url"].isin(shared)].groupby("libguide_url").size()
    ratio = (new_counts / old_counts).sort_values()
    dropped = ratio[ratio < ROW_DROP_WARN]
    if len(dropped):
        warn(f"{len(dropped)} guides lost >{ROW_DROP_WARN:.0%} of their baseline rows "
             "(possible parsing gaps):")
        for url, r in dropped.head(15).items():
            print(f"        {r:.0%} of baseline  {url}")
    else:
        ok(f"No shared guide lost more than {ROW_DROP_WARN:.0%} of its baseline rows")

    gone = set(old["libguide_url"]) - set(df["libguide_url"])
    if gone:
        warn(f"{len(gone)} baseline guides absent from the new scrape "
             "(removed, renamed, or failed):")
        for url in sorted(gone)[:15]:
            print(f"        {url}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--input", default=None, help="Scraped CSV to validate", dest = "guide_text_csv")
    parser.add_argument("--baseline", default=None, dest = "baseline_guide_text_csv",
                        help="Previous corpus CSV to compare against")
    parser.add_argument("--url-list", default=None)
    parser.add_argument("--no-baseline", action="store_true",
                        help="Skip the baseline comparison")
    args = parser.parse_args()

    # use command line args to override defaults:
    overrides = {
        key: value
        for key, value in vars(args).items()
        if value is not None
    }
    settings = load_settings(overrides)

    print(f"Validating {settings.guide_text_csv}")
    df = pd.read_csv(settings.guide_text_csv, encoding="utf-8")
    print(f"{len(df)} rows")

    check_schema(df)
    check_content(df)
    check_authors(df)
    check_coverage(df, settings.url_list_path)
    if not args.no_baseline:
        check_against_baseline(df, settings.baseline_guide_text_csv)

    print(f"\n{'=' * 50}")
    print(f"RESULT: {len(failures)} failures, {len(warnings)} warnings")
    if failures:
        print("Validation FAILED — do not feed this CSV to build_chromadb.py")
        sys.exit(1)
    print("Validation passed")


if __name__ == "__main__":
    main()
