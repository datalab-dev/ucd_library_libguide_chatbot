"""
- Fetch main libguide page
- Extract hrefs using XPath
- Normalizes relative URLs to absolute
- Stores unique URLs in a local SQLite database
"""

from pathlib import Path
from typing import List, Any
from urllib.parse import urljoin, urlparse, urlunparse
import re
import logging
import time

import requests
import pandas as pd



# Config
ROOT = "https://guides.library.ucdavis.edu/" #all guides
API_ACTION = 170
SITE_ID = 21608

# where to put CSV snapshot of the df
CSV_PATH = Path("/dsl/libbot/data/url_list.csv")

HEADERS = {"User-Agent": "DataLab libguidecrawler/1.0 (+https://github.com/datalab-dev/)"}
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")





# HTTP fetch helper
def fetch_page(url: str, session: requests.Session) -> str:
    # Fetch page HTML text using a requests.Session.
    # Raises an exception on HTTP errors (via raise_for_status()).
    
    logging.info(f"Fetching index page: {url}") # log the URL fetch
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text

# compiled regexes once
HREF_RE = re.compile(r'href=[\'"]([^\'"]+)[\'"]', flags=re.IGNORECASE)
ABS_URL_RE = re.compile(r'^https?://', flags=re.IGNORECASE)
SLUG_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9\-_]*/?[A-Za-z0-9\-_]+$')  # short slug-like token


def fetch_guides_via_api(base_site_url: str = ROOT, action: int = API_ACTION, site_id: int = SITE_ID) -> List[str]:
    """Call index_process.php and return a list of candidate URL strings (not yet fully cleaned)."""
    api_url = urljoin(base_site_url, "index_process.php")
    params = {"action": str(action), "site_id": str(site_id)}
    s = requests.Session()
    s.headers.update(HEADERS)
    logging.info("Calling API %s params=%s", api_url, params)
    resp = s.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    raw_links: List[str] = []

    def walk(obj: Any):
        if isinstance(obj, dict):
            # prefer obvious fields
            for k in ("url", "href", "link", "slug", "guide_url", "guide_link"):
                if k in obj and isinstance(obj[k], str) and obj[k].strip():
                    raw_links.append(obj[k].strip())
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, str):
            s = obj.strip()
            if not s:
                return
            # extract hrefs if the string contains embedded HTML
            if ("<" in s and ">" in s) or "href=" in s:
                for href in HREF_RE.findall(s):
                    raw_links.append(href.strip())
                return
            if len(s) > 200 or "\n" in s:
                return
            if ABS_URL_RE.match(s):
                raw_links.append(s)
                return
            if s.startswith("/"):
                raw_links.append(s)
                return
            if "libguides" in s.lower():
                raw_links.append(s)
                return
            if SLUG_RE.match(s):
                raw_links.append(s)
                return
            return

    walk(data)

    # normalize to absolute and dedupe preserving order
    out: List[str] = []
    seen = set()
    for c in raw_links:
        if not c:
            continue
        abs_url = urljoin(base_site_url, c)
        if not abs_url.startswith(("http://", "https://")):
            continue
        if "<" in abs_url or ">" in abs_url or len(abs_url) > 300:
            continue
        if abs_url not in seen:
            seen.add(abs_url)
            out.append(abs_url)
    return out


# cleaning/dedupe for df insertion
def clean_urls(urls: List[str]) -> List[str]:
    seen = set()
    out = []
    for u in urls:
        if not u:
            continue
        u = u.strip()
        p = urlparse(u)
        u = urlunparse(p._replace(fragment=""))
        # skip mailto/javascript
        if u.lower().startswith(("mailto:", "javascript:")):
            continue
        # require http(s)
        if not (u.startswith("http://") or u.startswith("https://")):
            continue
        # optional extra: require /libguides/ in path to be very strict
        # if "/libguides/" not in u.lower(): continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out




# Dataframe helper
def load_existing_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["url"])
    df = pd.read_csv(path, dtype={"url": str})
    # If the CSV has an 'id' column, drop it — we'll recreate ids ourselves
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    # Ensure we only return the 'url' column as a DataFrame
    if "url" not in df.columns:
        raise ValueError(f"{path} has no 'url' column")
    return df[["url"]].copy()


def save_df(df: pd.DataFrame, csv_path: Path = CSV_PATH):
    # ensure parent exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)


def main():
    
    # FETCH LINKS VIA
    try:
        raw_links = fetch_guides_via_api()
    except Exception as e:
        logging.error(f"API fetch failed: {e}. Exiting.")
        return
    logging.info("API returned %d candidate strings", len(raw_links))

    # CLEAN AND NORMALIZE LINKS
    cleaned = clean_urls(raw_links)
    logging.info("%d cleaned candidate URLs after normalization", len(cleaned))
    
    # LOAD EXISTING CSV (if any)
    existing_df = load_existing_csv(CSV_PATH)
    existing_urls = set(existing_df["url"].dropna().astype(str).tolist())
    logging.info("Existing CSV has %d URLs", len(existing_urls))

    # NEW URLS TO APPEND
    new_urls = [u for u in cleaned if u not in set(existing_df["url"].dropna().astype(str).tolist())]
    logging.info("Found %d new URLs to add", len(new_urls))

    if new_urls:
        append_df = pd.DataFrame({"url": new_urls})
        combined = pd.concat([existing_df, append_df], ignore_index=True, sort=False)
    else:
        combined = existing_df.copy()

    # DEAL WITH DUPLICATES
    if "id" in combined.columns:
        combined = combined.drop(columns=["id"])

    combined = combined.drop_duplicates(subset="url", keep="first").reset_index(drop=True)
    combined.insert(0, "id", range(1, len(combined) + 1))


    # SAVING DF to CSV
    save_df(combined, CSV_PATH)
    logging.info("Wrote %d rows to %s", len(combined), CSV_PATH)
    
    time.sleep(DELAY_BETWEEN_REQUESTS)


if __name__ == "__main__":
    main()
