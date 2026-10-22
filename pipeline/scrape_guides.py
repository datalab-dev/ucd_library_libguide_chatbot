"""Scrape UC Davis LibGuides into the 8-column corpus CSV.

Reads url_list.csv (id, url), walks every guide's sub-pages, and writes
text_full_libguide_new.csv with the schema expected by the rest of the
pipeline (see PIPELINE_PLAN.md, "Integration Contract"):

    local_id, parent_id, text, libguide_title, libguide_url,
    chunk_title, chunk_url, external_url

Row granularity matches the original Feb 2025 corpus: one row per
resource link (database/link/book asset) with its description as `text`.
Additionally, box-level prose with no asset link is emitted as rows with
an empty `external_url` (the original R scrape dropped these).

The `authors` column holds a JSON array (same value on every row of a
guide) of the librarian profiles shown in the guide's sidebar box
(usually "Research Support"). The page embeds only an email in a
<ucdlib-author-profile> web component; name and profile_url are resolved
through the library directory API the component itself calls.

Usage:
    pixi run python pipeline/scrape_guides.py
    pixi run python pipeline/scrape_guides.py --limit 5 --verbose
"""

import argparse
import csv
import json
import logging
import re
import sys
import time
from collections import Counter
from urllib.parse import parse_qs, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

# # ---------- Defaults ----------
# URL_LIST_PATH = "/dsl/libbot/data/url_list.csv"
# OUTPUT_PATH = "/dsl/libbot/data/text_full_libguide_new.csv"
# REQUEST_DELAY = 0.3  # seconds between HTTP requests
# REQUEST_TIMEOUT = 30.0
# MAX_RETRIES = 3
# USER_AGENT = (
#     "LibBot-scraper/1.0 (UC Davis Library DataLab; fgaprile@ucdavis.edu)"
# )
# MIN_PROSE_CHARS = 40  # ignore box prose shorter than this
# # ------------------------------

GUIDES_HOST = "guides.library.ucdavis.edu"

log = logging.getLogger("scrape_guides")


def clean_text(text: str) -> str:
    """Normalize unicode/whitespace (same rules as research/text_cleaning.py)."""
    text = str(text)
    text = text.replace("\xa0", " ")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class Fetcher:
    """HTTP client with retries and a politeness delay between requests."""

    def __init__(self, delay: float):
        self.delay = delay
        self.client = httpx.Client(
            follow_redirects=True,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        self._last_request = 0.0

    def get(self, url: str) -> httpx.Response | None:
        """Fetch a URL; returns None after MAX_RETRIES failures."""
        for attempt in range(1, MAX_RETRIES + 1):
            wait = self.delay - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()
            try:
                resp = self.client.get(url)
                if resp.status_code == 200:
                    return resp
                log.warning("HTTP %s for %s (attempt %d)", resp.status_code, url, attempt)
                if resp.status_code in (403, 404, 410):
                    return None  # retrying won't help
            except httpx.HTTPError as exc:
                log.warning("Error fetching %s (attempt %d): %s", url, attempt, exc)
            time.sleep(attempt * 2)
        return None

    def close(self):
        self.client.close()


def normalize_url(url: str) -> str:
    """Strip fragments and trailing slashes for comparison/dedup."""
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    base = f"{parsed.scheme}://{parsed.netloc}{path}"
    if parsed.query:
        base += f"?{parsed.query}"
    return base


def extract_guide_id(html: str) -> str | None:
    """Pull the numeric LibGuides guide id embedded in the page source.

    Guides embed it in varying forms ("guide_id":123, guide_id=123, ...),
    so match loosely and take the most frequent value.
    """
    matches = re.findall(r"guide_id\D{0,5}?(\d+)", html)
    if not matches:
        return None
    return Counter(matches).most_common(1)[0][0]


def find_subpage_urls(soup: BeautifulSoup, page_url: str, guide_id: str | None) -> list[str]:
    """Return same-guide sub-page URLs from the tab navigation, in order.

    A nav link belongs to this guide if its path starts with the guide's
    base path (friendly URLs) or it is a c.php link whose g= parameter
    matches the guide's own id. The currently active tab is skipped since
    its content is already on the page being parsed.
    """
    nav = soup.select_one("#s-lg-guide-tabs") or soup.select_one("#s-lg-tabs-container")
    if nav is None:
        return []

    base_path = urlparse(page_url).path.rstrip("/")
    # On a sub-page like /ABG-202/databases the guide base path is /ABG-202
    parts = [p for p in base_path.split("/") if p]
    if parts and parts[0] != "c.php":
        guide_path = "/" + parts[0]
    else:
        guide_path = base_path

    urls = []
    for a in nav.find_all("a", href=True):
        li = a.find_parent("li")
        if li and "active" in (li.get("class") or []):
            continue
        href = urljoin(page_url, a["href"])
        parsed = urlparse(href)
        if parsed.netloc != GUIDES_HOST:
            continue
        if parsed.path.startswith("/c.php"):
            g = parse_qs(parsed.query).get("g", [None])[0]
            if guide_id is None or g != guide_id:
                continue
        elif not parsed.path.rstrip("/").startswith(guide_path):
            continue
        url = normalize_url(href)
        if url not in urls:
            urls.append(url)
    return urls


DIRECTORY_API_PATH = "/wp-json/ucdlib-directory/person/"
DEFAULT_DIRECTORY_HOST = "https://library.ucdavis.edu"

# email -> resolved author dict, shared across guides (the same librarian
# appears in many guides' sidebars)
_author_cache: dict[str, dict] = {}


def resolve_author(fetcher: Fetcher, email: str, host: str) -> dict:
    """Look up an author profile in the library directory API."""
    key = email.lower()
    if key in _author_cache:
        return _author_cache[key]

    author = {"name": "", "profile_url": "", "email": email}
    resp = fetcher.get(f"{host.rstrip('/')}{DIRECTORY_API_PATH}{email}")
    if resp is not None:
        try:
            data = resp.json()
            name = f"{data.get('nameFirst', '')} {data.get('nameLast', '')}".strip()
            author["name"] = name
            author["profile_url"] = data.get("link") or ""
        except ValueError:
            log.warning("Directory API returned non-JSON for %s", email)
    else:
        log.warning("Could not resolve author profile for %s", email)
    _author_cache[key] = author
    return author


def collect_authors(fetcher: Fetcher, pages: list[tuple[str, BeautifulSoup]]) -> list[dict]:
    """Find sidebar author profiles across a guide's pages, in page order."""
    authors, seen = [], set()
    for _, page_soup in pages:
        for el in page_soup.find_all("ucdlib-author-profile"):
            email = (el.get("email") or "").strip()
            if not email or email.lower() in seen:
                continue
            seen.add(email.lower())
            host = (el.get("host") or "").strip() or DEFAULT_DIRECTORY_HOST
            authors.append(resolve_author(fetcher, email, host))
    return authors


def get_guide_title(soup: BeautifulSoup) -> str:
    el = soup.select_one("#s-lg-guide-name") or soup.select_one("h1")
    return el.get_text(strip=True) if el else ""


def _strip_noise(element):
    """Remove hidden/decorative markup before extracting visible text."""
    for tag in element.find_all(["script", "style", "noscript", "button", "img"]):
        tag.decompose()
    for cls in ("sr-only", "s-lg-content-more-info", "s-lg-label-moreinfo",
                "s-lg-label-more-info", "s-lg-icons"):
        for tag in element.find_all(class_=cls):
            tag.decompose()


def parse_boxes(soup: BeautifulSoup, page_url: str) -> list[dict]:
    """Extract chunks from every content box on a page.

    Returns dicts with keys: chunk_title, chunk_url, external_url, text.
    """
    # Fallback section title for untitled boxes: the page/tab name, taken
    # from <title> "Page - Guide - Research Guides at UC Davis"
    page_title = ""
    if soup.title:
        page_title = soup.title.get_text(strip=True).split(" - ")[0].strip()

    chunks = []
    for box in soup.select(".s-lib-box"):
        title_el = box.select_one(".s-lib-box-title")
        box_title = title_el.get_text(strip=True) if title_el else page_title
        content = box.select_one(".s-lib-box-content")
        if content is None:
            continue
        _strip_noise(content)

        # Asset rows: one per resource link with a description. As in the
        # original corpus, chunk_title is the resource's own name. Assets
        # without a description are left in the tree so their titles appear
        # in the box's prose row instead of becoming empty rows.
        for div in content.select("div[id^=s-lg-content-]"):
            anchor = div.find("a", href=True)
            if anchor is None:
                continue
            desc_el = div.find("div", class_=re.compile(r"desc"))
            desc = desc_el.get_text(" ", strip=True) if desc_el else ""
            if not desc:
                continue
            link_title = anchor.get_text(" ", strip=True)
            chunks.append({
                "chunk_title": link_title,
                "chunk_url": page_url,
                "external_url": urljoin(page_url, anchor["href"]),
                "text": desc,
            })
            # Remove from the tree so prose extraction below doesn't re-read it
            li = div.find_parent("li")
            (li or div).decompose()

        # Prose row: whatever visible text remains in the box
        prose = content.get_text(" ", strip=True)
        if len(prose) >= MIN_PROSE_CHARS:
            chunks.append({
                "chunk_title": box_title,
                "chunk_url": page_url,
                "external_url": "",
                "text": prose,
            })
    return chunks


def scrape_guide(fetcher: Fetcher, guide_id_csv: int, guide_url: str) -> list[dict]:
    """Scrape one guide (home page + all sub-pages) into row dicts."""
    resp = fetcher.get(guide_url)
    if resp is None:
        log.error("SKIPPING guide %s — could not fetch %s", guide_id_csv, guide_url)
        return []

    home_url = normalize_url(str(resp.url))
    if urlparse(home_url).netloc != GUIDES_HOST:
        log.error("SKIPPING guide %s — %s redirects off LibGuides to %s",
                  guide_id_csv, guide_url, home_url)
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    libguide_title = get_guide_title(soup)
    lg_guide_id = extract_guide_id(resp.text)

    page_urls = find_subpage_urls(soup, home_url, lg_guide_id)

    rows = []
    seen_pages = {home_url}
    pages = [(home_url, soup)]
    for url in page_urls:
        if url in seen_pages:
            continue
        seen_pages.add(url)
        sub_resp = fetcher.get(url)
        if sub_resp is None:
            log.error("Skipping page %s of guide %s", url, guide_id_csv)
            continue
        final = normalize_url(str(sub_resp.url))
        if final != url and final in seen_pages:
            continue
        seen_pages.add(final)
        pages.append((final, BeautifulSoup(sub_resp.text, "html.parser")))

    authors_json = json.dumps(collect_authors(fetcher, pages), ensure_ascii=False)

    for page_url, page_soup in pages:
        for chunk in parse_boxes(page_soup, page_url):
            text = clean_text(chunk["text"])
            if not text:
                continue
            rows.append({
                "parent_id": guide_id_csv,
                "text": text,
                "libguide_title": clean_text(libguide_title),
                "libguide_url": home_url,
                "chunk_title": clean_text(chunk["chunk_title"]),
                "chunk_url": chunk["chunk_url"],
                "external_url": chunk["external_url"],
                "authors": authors_json,
            })

    log.info("Guide %s (%s): %d pages, %d chunks, %d authors",
             guide_id_csv, libguide_title or guide_url, len(pages), len(rows),
             authors_json.count('"email"'))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--url-list", default=None,
                        help="CSV of guides to scrape (id,url)")
    parser.add_argument("--output", default=None, dest="guide_text_csv",
                        help="Output CSV path")
    parser.add_argument("--delay", type=float, default=None,
                        help="Seconds between HTTP requests")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only scrape the first N guides (for testing)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # use command line args to override defaults:
    overrides = {
        key: value
        for key, value in vars(args).items()
        if value is not None
    }
    settings = load_settings(overrides)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stderr,
    )
    if not args.verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    with open(args.url_list, newline="", encoding="utf-8") as f:
        guides = [(int(row["id"]), row["url"]) for row in csv.DictReader(f)]
    if args.limit:
        guides = guides[: args.limit]
    log.info("Scraping %d guides from %s", len(guides), args.url_list)

    fetcher = Fetcher(delay=args.delay)
    all_rows = []
    failed_guides = []
    started = time.monotonic()
    try:
        for i, (gid, url) in enumerate(guides, 1):
            rows = scrape_guide(fetcher, gid, url)
            if rows:
                all_rows.extend(rows)
            else:
                failed_guides.append((gid, url))
            if i % 25 == 0:
                log.info("Progress: %d/%d guides, %d chunks, %.0fs elapsed",
                         i, len(guides), len(all_rows), time.monotonic() - started)
    finally:
        fetcher.close()

    fieldnames = ["local_id", "parent_id", "text", "libguide_title",
                  "libguide_url", "chunk_title", "chunk_url", "external_url",
                  "authors"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for local_id, row in enumerate(all_rows, 1):
            writer.writerow({"local_id": local_id, **row})

    elapsed = time.monotonic() - started
    log.info("Done in %.0fs: %d chunks from %d/%d guides -> %s",
             elapsed, len(all_rows), len(guides) - len(failed_guides),
             len(guides), args.output)
    if failed_guides:
        log.warning("Guides with no content (%d):", len(failed_guides))
        for gid, url in failed_guides:
            log.warning("  id=%s %s", gid, url)


if __name__ == "__main__":
    main()
