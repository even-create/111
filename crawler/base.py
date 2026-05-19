from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}


def fetch(url):
    """Fetch a page and return decoded HTML."""
    res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    if not res.encoding or res.encoding.lower() == "iso-8859-1":
        res.encoding = res.apparent_encoding or "utf-8"
    return res.text


def parse_html(html):
    return BeautifulSoup(html, "lxml")


def normalize_link(base_url, link):
    return urljoin(base_url, link.strip())
