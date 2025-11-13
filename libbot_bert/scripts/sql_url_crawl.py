"""
- Fetch main libguide page
- Extract hrefs using XPath
- Normalizes relative URLs to absolute
- Stores unique URLs in a local SQLite database
"""

import time
import logging
import sqlite3
from typing import List, Any
from urllib.parse import urljoin, urlparse, urlunparse
from pathlib import Path
import re
import requests
from lxml import html
import pandas as pd




# Config
INDEX_URL = "https://guides.library.ucdavis.edu/" # list of guides
DB_PATH = Path("/dsl/libbot/data/url_database.db") # database location as a Path
HEADERS = { # rquests specifications
    "User-Agent": "DataLab libguidecrawler/1.0 (+https://github.com/datalab-dev/2025_startup_libguide_chatbot/)"
}
REQUEST_TIMEOUT = 15
DELAY_BETWEEN_REQUESTS = 2

# API params discovered in the site's JS (chatgpt help on this)
API_ACTION = 170
SITE_ID = 21608


# logging fetches and other events
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
SLUG_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9\-_]*/?[A-Za-z0-9\-_]+$')  # short-ish slug or token

def fetch_guides_via_api(base_site_url: str = INDEX_URL, action: int = API_ACTION, site_id: int = SITE_ID) -> List[str]:
    """
    Call the site's API and return a deduplicated list of ABSOLUTE URLs (http(s) or root-relative turned absolute).
    This version aggressively avoids adding HTML fragments or long text blobs.
    """
    api_url = urljoin(base_site_url, "index_process.php")
    params = {"action": str(action), "site_id": str(site_id)}
    s = requests.Session()
    s.headers.update(HEADERS)
    resp = s.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    candidates: List[str] = []

    def walk(o: Any):
        """Recursively walk JSON and collect *candidate* strings."""
        if isinstance(o, dict):
            # prefer obvious fields first
            for k in ("url", "href", "link", "slug", "guide_url", "guide_link"):
                if k in o and isinstance(o[k], str) and o[k].strip():
                    candidates.append(o[k].strip())
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for item in o:
                walk(item)
        elif isinstance(o, str):
            s = o.strip()
            if not s:
                return
            # If the string looks like embedded HTML, extract href attributes inside it (if any)
            if ("<" in s and ">" in s) or "href=" in s:
                for href in HREF_RE.findall(s):
                    candidates.append(href.strip())
                return
            # Skip strings that are huge or have newlines (likely text blobs)
            if len(s) > 200 or "\n" in s:
                return
            # If it's an absolute URL, keep
            if ABS_URL_RE.match(s):
                candidates.append(s)
                return
            # If it's a root-relative path, keep
            if s.startswith("/"):
                candidates.append(s)
                return
            # If it looks like a short slug token (e.g., ABG-202 or some/slug), accept
            if SLUG_RE.match(s):
                candidates.append(s)
                return
            # else ignore
            return

    walk(data)

    # Normalize to absolute and dedupe preserving order
    out: List[str] = []
    seen = set()
    for c in candidates:
        if not c:
            continue
        abs_url = urljoin(base_site_url, c)
        # sanity: only http/s
        if not abs_url.startswith(("http://", "https://")):
            continue
        # final sanity: no angle brackets, not excessively long
        if "<" in abs_url or ">" in abs_url or len(abs_url) > 300:
            continue
        if abs_url not in seen:
            seen.add(abs_url)
            out.append(abs_url)
    return out


# # parsing helper
# def parse_links_with_xpath(html_text: str, base_url: str, xpath_expr: str) -> List[str]:
#     # parse HTML text using lxml and extract hrefs using the XPath that's in main()
#     # xpath_expr should select href attributes
    
#     tree = html.fromstring(html_text)
#     raw_hrefs = tree.xpath(xpath_expr)
#     # normalize to absolute URLs
#     abs_hrefs = [urljoin(base_url, href) for href in raw_hrefs if href and isinstance(href, str)]
#     return abs_hrefs


# cleaning + dedupe
def clean_urls(urls: List[str]) -> List[str]:
    seen = set()
    out = []
    for u in urls:
        if not u:
            continue
        u = u.strip()
        # parse and remove fragment (after '#')
        p = urlparse(u)
        u = urlunparse(p._replace(fragment=""))
        # skip obvious non-http schemes
        if u.lower().startswith(("mailto:", "javascript:")):
            continue
        # skip empty or malformed scheme-less strings
        if not (u.startswith("http://") or u.startswith("https://")):
            # still allow root-relative like "/libguides/..." (these should have been urljoined earlier)
            # if it's still not http(s) at this point, skip it
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out



# SQLite helpers (used chatgpt mainly for this part because I'm not familiar with SQLite)
def ensure_db_and_table(db_path: Path):
    
    """
    Ensure parent directory exists, create the SQLite file if missing,
    and create the 'urls' table if it doesn't already exist.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                status INTEGER,
                last_fetched TIMESTAMP,
                html_path TEXT,
                text_path TEXT
            )
            """
        )
        conn.commit()


def insert_urls(db_path: Path, urls: List[str], source: str = None) -> int:
    """
    Insert new URLs into the DB. Returns number of inserted rows (new URLs).
    Uses 'INSERT OR IGNORE' to avoid duplicates.
    """
    if not urls:
        return 0
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        before = conn.total_changes
        for u in urls:
            try:
                cur.execute("INSERT OR IGNORE INTO urls (url, source) VALUES (?, ?)", (u, source))
            except sqlite3.Error as e:
                logging.warning(f"SQLite error inserting {u}: {e}")
        conn.commit()
        after = conn.total_changes
    return after - before



def get_all_urls(db_path: Path) -> List[str]:
    """
    Return all URLs from the DB ordered by insertion id.
    """
    with sqlite3.connect(str(db_path)) as conn:
        df = pd.read_sql_query("SELECT url FROM urls ORDER BY id", conn)
    return df["url"].tolist()


def main():
    # prepare DB
    ensure_db_and_table(DB_PATH)

    # prepare HTTP session with the headers
    # s = requests.Session()
    # s.headers.update(HEADERS)


    #trying to fetch via API
    try:
        raw_links = fetch_guides_via_api()
    except Exception as e:
        logging.error(f"API fetch failed: {e}. Exiting.")
        return

    logging.info(f"API returned {len(raw_links)} candidate links (before cleaning).")

    # Clean & dedupe using same helper
    picks = clean_urls(raw_links)
    logging.info(f"{len(picks)} links remain after cleaning/dedupe.")

    # Insert into DB
    new_count = insert_urls(DB_PATH, picks, source=f"api?action={API_ACTION}&site_id={SITE_ID}")
    logging.info(f"Inserted {new_count} new URLs into {DB_PATH}")

    # write snapshot CSV
    all_urls = get_all_urls(DB_PATH)
    csv_out = DB_PATH.with_suffix(".csv")
    pd.DataFrame({"url": all_urls}).to_csv(csv_out, index=False)
    logging.info(f"Wrote CSV snapshot with {len(all_urls)} URLs to {csv_out}")

    time.sleep(DELAY_BETWEEN_REQUESTS)


if __name__ == "__main__":
    main()
