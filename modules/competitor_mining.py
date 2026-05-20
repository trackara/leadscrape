"""
modules/competitor_mining.py
----------------------------
Scrape competitor luxury hotels' websites for their published partner / trade /
travel-professional pages. The agencies listed there are pre-qualified buyers
of luxury Mediterranean travel — much higher conversion than generic search.

Use case: paste the URL of a comparable hotel (Borgo Egnazia, Maslina, Aman
Sveti Stefan, Cap Rocat, etc.) → get back the agencies they work with → run
those through the standard enrichment pipeline.
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# We rely on pipeline.py for HTTP fetching + URL normalization
from pipeline import fetch_url, normalize_domain

log = logging.getLogger("competitor_mining")


# Common URL paths where hotels publish their trade/partner info.
# Order is rough priority — most hotels use one of the top three.
TRADE_PATHS = [
    "/trade", "/travel-trade", "/travel-professionals",
    "/trade-professionals", "/travel-agents", "/agents",
    "/partners", "/travel-partners", "/preferred-partners",
    "/travel-advisors", "/advisors",
    "/press", "/media", "/press-room",
]

# Domains we never count as "discovered partners" — they're not agencies
NON_AGENCY_DOMAINS = [
    "facebook.", "instagram.", "linkedin.", "twitter.", "x.com",
    "youtube.", "tiktok.", "pinterest.", "vimeo.",
    "wikipedia.", "wikidata.",
    "google.", "bing.", "apple.com", "maps.google.",
    "tripadvisor.", "booking.com", "expedia.", "hotels.com", "airbnb.",
    "small luxury hotels", "slh.com",   # the hotel's own consortium
    "virtuoso.com",  # this is interesting but it's a network, not an agency
    "amazon.", "youtu.be",
    "fontawesome.", "googletagmanager.", "google-analytics.",
    "cookiebot.", "iubenda.",
]


def find_trade_pages(hotel_url: str) -> list[tuple[str, str]]:
    """Probe TRADE_PATHS on the hotel's domain. Return [(url, html), ...] for ones that load.
    Always includes the homepage as a fallback.
    """
    parsed = urlparse(hotel_url)
    if not parsed.netloc:
        return []
    base = f"{parsed.scheme or 'https'}://{parsed.netloc}"

    found: list[tuple[str, str]] = []

    # Always start with homepage — sometimes partners are linked from the footer
    home_html = fetch_url(base)
    if home_html:
        found.append((base, home_html))

    for path in TRADE_PATHS:
        url = urljoin(base, path)
        html = fetch_url(url)
        if html:
            found.append((url, html))

    return found


def is_agency_link(href: str, text: str, source_domain: str) -> bool:
    """Heuristic: does this <a> link to a candidate partner agency?"""
    if not href or not text:
        return False
    if len(text.strip()) < 3 or len(text) > 100:
        return False

    parsed = urlparse(href)
    domain = (parsed.netloc or "").lower()
    if not domain:
        return False
    # Skip same-domain links (internal navigation)
    if source_domain in domain or domain in source_domain:
        return False
    # Skip non-agency domains
    if any(b.lower() in domain for b in NON_AGENCY_DOMAINS):
        return False
    # Skip mail / tel / javascript links
    if parsed.scheme in ("mailto", "tel", "javascript"):
        return False
    # Skip image links
    if any(href.lower().endswith(ext) for ext in [".jpg", ".png", ".pdf", ".gif", ".svg"]):
        return False
    return True


def extract_agencies(pages: list[tuple[str, str]]) -> list[dict]:
    """Across all fetched pages, find external links that look like partner agencies.
    Returns deduped list: [{"name": ..., "url": ..., "source_page": ...}, ...]
    """
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
                "source_page": source_url,
                "source_hotel": source_domain,
            })
    return out


def mine_competitor(hotel_url: str, progress_callback=None) -> list[dict]:
    """Top-level: given a hotel URL, return list of partner agencies linked from it."""
    if progress_callback:
        progress_callback(f"Scanning {hotel_url}")
    pages = find_trade_pages(hotel_url)
    if not pages:
        log.warning(f"No trade pages found on {hotel_url}")
        return []
    if progress_callback:
        progress_callback(f"Extracting partners from {len(pages)} page(s)")
    return extract_agencies(pages)
