"""
- Fetch main libguide page
- Extract hrefs using XPath
- Normalizes relative URLs to absolute
- Stores unique URLs in a local SQLite database
"""

import time
import logging
import sqlite3
from typing import List, Set
from urllib.parse import urljoin, urlparse, urlunparse
from pathlib import Path

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



# parsing helper
def parse_links_with_xpath(html_text: str, base_url: str, xpath_expr: str) -> List[str]:
    # parse HTML text using lxml and extract hrefs using the XPath that's in main()
    # xpath_expr should select href attributes
    
    tree = html.fromstring(html_text)
    raw_hrefs = tree.xpath(xpath_expr)
    # normalize to absolute URLs
    abs_hrefs = [urljoin(base_url, href) for href in raw_hrefs if href and isinstance(href, str)]
    return abs_hrefs


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
    s = requests.Session()
    s.headers.update(HEADERS)

    # fetch index
    try:
        idx_html = fetch_page(INDEX_URL, s)
    except Exception as e:
        logging.error(f"Failed to fetch index page: {e}")
        return

    # xpath to grab the correct links
    xpath_expr = '//div[@class="s-lib-box s-lib-border-round s-lib-box-idx-guide-list"]//a[@class="bold"]/@href'


    # extract raw hrefs and run them through the url cleaning function
    raw_links = parse_links_with_xpath(idx_html, INDEX_URL, xpath_expr)
    logging.info(f"Found {len(raw_links)} raw links on the index page.")
    picks = clean_urls(raw_links)
    logging.info(f"Found {len(raw_links)} raw links on the index page.")




    # insert into DB
    new_count = insert_urls(DB_PATH, picks, source=INDEX_URL)
    logging.info(f"Inserted {new_count} new URLs into {DB_PATH}")

    # dump a CSV snapshot for easy use later
    all_urls = get_all_urls(DB_PATH)
    csv_out = DB_PATH.with_suffix(".csv")
    pd.DataFrame({"url": all_urls}).to_csv(csv_out, index=False)
    logging.info(f"Wrote CSV snapshot with {len(all_urls)} URLs to {csv_out}")

    # polite delay before finishing
    time.sleep(DELAY_BETWEEN_REQUESTS)


if __name__ == "__main__":
    main()
