"""
modules/directories.py
----------------------
Industry directory scraper. Designed to extract member listings from public
directory pages (luxury travel network member lists, association directories,
press / "as seen in" pages).

Realistic limits:
  - Most premium directories (Virtuoso, ASTA, Traveller Made full list) require
    login — those won't work and that's fine.
  - For PUBLIC pages, this gets you 70-90% of listed members in one click.

Use case: paste a directory URL → get a clean list of agencies + URLs → push
through the enrichment pipeline.
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from pipeline import fetch_url, normalize_domain
from modules.competitor_mining import is_agency_link, NON_AGENCY_DOMAINS

log = logging.getLogger("directories")


# Known publicly-scrapeable directory presets.
# Add more as you find ones that work without login.
KNOWN_DIRECTORIES = {
    "Travel + Leisure A-List (Italy)": (
        "https://www.travelandleisure.com/travel-advisors/region/europe/italy"
    ),
    "Conde Nast Traveler Top Travel Specialists": (
        "https://www.cntraveler.com/travel-specialists"
    ),
}


def scrape_directory(url: str, deep: bool = False, progress_callback=None) -> list[dict]:
    """Scrape a directory URL.

    deep=True: also follow obvious 'next page' / pagination links (one level).
    Returns: [{"name": ..., "url": ..., "source": directory_url}, ...]
    """
    if progress_callback:
        progress_callback(f"Loading {url}")

    html = fetch_url(url)
    if not html:
        log.warning(f"Could not load directory: {url}")
        return []

    pages_to_scan: list[tuple[str, str]] = [(url, html)]

    # Optionally follow pagination
    if deep:
        soup = BeautifulSoup(html, "lxml")
        pagination_links = _find_pagination_links(soup, url)
        for i, page_url in enumerate(pagination_links[:5]):  # cap at 5 extra pages
            if progress_callback:
                progress_callback(f"Loading page {i + 2}: {page_url}")
            extra_html = fetch_url(page_url)
            if extra_html:
                pages_to_scan.append((page_url, extra_html))

    return _extract_member_links(pages_to_scan)


def _find_pagination_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Look for obvious 'page 2', 'next' links."""
    links = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        text = a.get_text(strip=True).lower()
        # Common pagination signals
        if any(t in text for t in ["next", "weiter", "nächste", "page 2", "page 3"]):
            links.add(urljoin(base_url, href))
        if "?page=" in href or "/page/" in href:
            links.add(urljoin(base_url, href))
    return list(links)


def _extract_member_links(pages: list[tuple[str, str]]) -> list[dict]:
    """Find external company links across all pages. Deduped by domain."""
    seen_domains: set[str] = set()
    out: list[dict] = []

    for source_url, html in pages:
        soup = BeautifulSoup(html, "lxml")
        source_domain = urlparse(source_url).netloc.lower()
        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            text = a.get_text(strip=True)
            if not is_agency_link(href, text, source_domain):
                continue
            absolute = urljoin(source_url, href)
            domain = normalize_domain(absolute)
            if not domain or domain in seen_domains:
                continue
            seen_domains.add(domain)
            out.append({
                "name": text[:100],
                "url": absolute,
                "source": source_url,
            })
    return out
