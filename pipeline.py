"""
pipeline.py
-----------
Free lead-generation pipeline. No paid APIs.

Flow:
  1. DuckDuckGo Search → list of candidate URLs (no API key required)
  2. Filter URLs through domain blacklist + existing-partners list
  3. Visit each surviving URL → extract company name, email, phone, address, description
  4. OpenStreetMap Nominatim → geocode the address to lat/lng + city/country
  5. Auto-qualify based on keywords

Designed to be importable by app.py (Streamlit UI) but also runnable standalone.
"""

from __future__ import annotations

import re
import time
import logging
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("pipeline")


# ---------- Data model ----------

@dataclass
class Lead:
    company: str = ""
    segment: str = ""           # which segment label produced this lead
    address: str = ""
    city: str = ""
    country: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    specialization: str = ""    # one-sentence relevance
    latitude: float | None = None
    longitude: float | None = None
    fit_score: int | None = None      # auto-computed 1-5
    status: str = "Needs Review"      # Qualified / Needs Review / Disqualified
    existing_partner: bool = False
    attends_fam: bool = False         # detected on the website (FAM trip / familiarization)
    is_new: bool = True               # set by dedup_db on annotation
    previously_seen: str = ""         # ISO date if already in DB
    source: str = "search"            # 'search' | 'competitor' | 'directory'
    notes: str = ""


# ---------- Regexes ----------

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(
    r"(?:\+|00)\s?\d{1,3}[\s\-\(\)]*(?:\d[\s\-\(\)]*){7,14}\d"
)
EMAIL_BLACKLIST = (
    "@sentry", "@example", "@wixpress", "noreply", "no-reply",
    ".png", ".jpg", ".gif", ".svg", "@2x", "u003",
)
CONTACT_PATHS = [
    "/kontakt", "/contact", "/kontakt/", "/contact/", "/contact-us",
    "/impressum", "/imprint", "/about", "/ueber-uns", "/about-us",
]

# Phrases on a website that suggest the agency runs / attends FAM (familiarization) trips.
# Strong signal that they invest in property visits → high-value outreach target.
FAM_KEYWORDS = [
    "fam trip", "famtrip", "fam-trip",
    "familiarization", "familiarisation",
    "site inspection", "site visit",
    "inforeise", "informationsreise",
    "viaggio di familiarizzazione",
    "agent stays", "agent rates",
]


def detect_fam(html: str) -> bool:
    """True if the page text mentions FAM / familiarization activity."""
    if not html:
        return False
    haystack = html.lower()
    return any(k in haystack for k in FAM_KEYWORDS)

# Address regex — matches things like "Hauptstraße 12, 80333 München"
# Or "Via Roma 1, 20100 Milano". Conservative; misses some formats.
ADDRESS_RE = re.compile(
    r"([A-ZÄÖÜÉÈÀÁÂÇ][\w\.\-äöüéèàáâç]{2,40}?\s+\d+[\w\-]?)[\s,]+(\d{4,5})\s+([A-ZÄÖÜÉÈÀÁÂÇ][\w\-äöüéèàáâç ]{2,40})",
    re.MULTILINE,
)


# ---------- DuckDuckGo search ----------

def ddg_search(query: str, max_results: int = 10) -> list[dict]:
    """Search via the `ddgs` package (formerly duckduckgo-search).
    Returns list of {title, href, body}. Tries the new package first, falls back
    to the legacy one, then to direct DuckDuckGo HTML scraping if both fail.
    """
    DDGS = None
    try:
        from ddgs import DDGS as _DDGS
        DDGS = _DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS as _DDGS
            DDGS = _DDGS
        except ImportError:
            log.warning("Neither `ddgs` nor `duckduckgo-search` is installed.")

    results: list[dict] = []
    if DDGS is not None:
        for attempt in range(2):
            try:
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=max_results, region="wt-wt"):
                        if "url" in r and "href" not in r:
                            r["href"] = r["url"]
                        results.append(r)
                if results:
                    return results
            except Exception as e:
                log.warning(f"DDG search attempt {attempt + 1} failed for '{query}': {e}")
                time.sleep(2)

    # Fallback: scrape html.duckduckgo.com directly
    if not results:
        log.info(f"Falling back to HTML scrape for '{query}'")
        results = ddg_html_search(query, max_results)
    return results


def ddg_html_search(query: str, max_results: int = 10) -> list[dict]:
    """Direct DuckDuckGo HTML endpoint scrape. Used when the API library is blocked."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
    }
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=headers,
            timeout=10,
        )
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "lxml")
        out = []
        for result in soup.select(".result")[:max_results]:
            link = result.select_one(".result__a")
            snippet = result.select_one(".result__snippet")
            if not link:
                continue
            href = link.get("href", "")
            # DDG wraps links in /l/?uddg=ENCODED
            if "uddg=" in href:
                from urllib.parse import unquote, parse_qs, urlparse as up
                qs = parse_qs(up(href).query)
                href = unquote(qs.get("uddg", [href])[0])
            out.append({
                "title": link.get_text(strip=True),
                "href": href,
                "body": snippet.get_text(strip=True) if snippet else "",
            })
        return out
    except Exception as e:
        log.warning(f"HTML fallback failed: {e}")
        return []


# ---------- URL filtering ----------

def normalize_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


def is_blacklisted(url: str, blacklist: list[str]) -> bool:
    domain = normalize_domain(url)
    return any(b.lower() in domain for b in blacklist)


def matches_existing_partner(url: str, company_name: str, partners: list[str]) -> bool:
    """Match against domains AND company-name fragments, case-insensitive."""
    domain = normalize_domain(url)
    company_lower = company_name.lower()
    for p in partners:
        p_low = p.lower().strip()
        if not p_low:
            continue
        if p_low in domain or p_low in company_lower:
            return True
    return False


# ---------- Website fetching ----------

def fetch_url(url: str, timeout: int = 8) -> str | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8,hr;q=0.7",
    }
    try:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        ct = r.headers.get("content-type", "")
        if r.status_code == 200 and "text/html" in ct:
            return r.text
    except Exception as e:
        log.debug(f"fetch_url failed for {url}: {e}")
    return None


# ---------- Extraction ----------

def extract_company_name(soup: BeautifulSoup, fallback_url: str) -> str:
    og = soup.find("meta", attrs={"property": "og:site_name"})
    if og and og.get("content"):
        return og["content"].strip()
    title = soup.find("title")
    if title and title.get_text(strip=True):
        # Drop the trailing " | Some Tagline" or " - Foo Bar"
        t = title.get_text(strip=True)
        for sep in [" | ", " - ", " – ", " — "]:
            if sep in t:
                t = t.split(sep)[0].strip()
                break
        return t[:80]
    return normalize_domain(fallback_url)


def extract_emails(html: str) -> list[str]:
    found = set(EMAIL_RE.findall(html))
    return [e for e in found if not any(b in e.lower() for b in EMAIL_BLACKLIST)]


def extract_phones(html: str) -> list[str]:
    return list(set(PHONE_RE.findall(html)))


def extract_specialization(soup: BeautifulSoup) -> str:
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content"):
        return _first_sentence(og["content"])
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return _first_sentence(meta["content"])
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 60:
            return _first_sentence(text)
    return ""


def _first_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    match = re.search(r"^(.{20,200}?[.!?])\s", text + " ")
    return (match.group(1) if match else text[:200]).strip()


def extract_address(html: str) -> str:
    """Best-effort: find a postal-address-looking string."""
    matches = ADDRESS_RE.findall(html)
    if matches:
        street, postal, city = matches[0]
        return f"{street.strip()}, {postal} {city.strip()}"
    return ""


def enrich_from_website(website: str) -> dict:
    """Visit homepage + likely contact pages. Returns dict with company info."""
    if not website:
        return {}

    parsed = urlparse(website)
    base = f"{parsed.scheme}://{parsed.netloc}"
    pages_to_try = [website] + [urljoin(base, p) for p in CONTACT_PATHS]

    company = ""
    specialization = ""
    address = ""
    emails: list[str] = []
    phones: list[str] = []
    attends_fam = False
    seen = set()

    for page_url in pages_to_try:
        if page_url in seen:
            continue
        seen.add(page_url)
        html = fetch_url(page_url)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")
        if not company:
            company = extract_company_name(soup, website)
        if not specialization:
            specialization = extract_specialization(soup)
        if not address:
            address = extract_address(html)
        if not attends_fam:
            attends_fam = detect_fam(html)

        emails.extend(extract_emails(html))
        phones.extend(extract_phones(html))

        if emails and phones and address and attends_fam:
            break
        time.sleep(0.4)

    emails = sorted(set(emails), key=len)
    return {
        "company": company,
        "specialization": specialization,
        "address": address,
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "attends_fam": attends_fam,
    }


# ---------- Geocoding (Nominatim) ----------

_last_nominatim_call = 0.0

def geocode(address: str, contact_email: str = "leadfinder@san-canzian.com") -> dict:
    """OpenStreetMap Nominatim geocoder. Free, 1 req/sec rate limit."""
    global _last_nominatim_call
    if not address:
        return {}

    # Polite rate limiting per OSM TOS
    elapsed = time.time() - _last_nominatim_call
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_nominatim_call = time.time()

    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1, "addressdetails": 1},
            headers={"User-Agent": f"LeadFinder/1.0 ({contact_email})"},
            timeout=10,
        )
        if r.ok and r.json():
            d = r.json()[0]
            addr = d.get("address", {})
            return {
                "latitude": float(d["lat"]),
                "longitude": float(d["lon"]),
                "city": addr.get("city") or addr.get("town") or addr.get("village") or "",
                "country": addr.get("country") or "",
            }
    except Exception as e:
        log.debug(f"geocode failed for '{address}': {e}")
    return {}


# ---------- Auto-qualification ----------

def auto_qualify(lead: Lead, target_keywords: list[str], anti_keywords: list[str] | None = None) -> tuple[str, int]:
    text = f"{lead.company} {lead.specialization}".lower()
    if anti_keywords is None:
        try:
            from config import ANTI_KEYWORDS
            anti_keywords = ANTI_KEYWORDS
        except ImportError:
            anti_keywords = ["inbound", "city tour", "stadtführung", "cruise", "youth", "party"]
    if any(a.lower() in text for a in anti_keywords):
        return ("Disqualified", 1)

    hits = sum(1 for k in target_keywords if k.lower() in text)
    if hits >= 2:
        return ("Qualified", 5)
    if hits == 1:
        return ("Qualified", 4)
    if lead.email or lead.phone:
        return ("Needs Review", 3)
    return ("Needs Review", 2)


# ---------- Top-level pipeline ----------

def run_pipeline(
    location: str,
    queries: list[tuple[str, str]],          # [(segment_label, search_query), ...]
    max_per_query: int = 8,
    target_keywords: list[str] | None = None,
    existing_partners: list[str] | None = None,
    domain_blacklist: list[str] | None = None,
    enrich_websites: bool = True,
    progress_callback=None,
) -> list[Lead]:
    target_keywords = target_keywords or []
    existing_partners = existing_partners or []
    domain_blacklist = domain_blacklist or []

    # ---- Phase 1: discovery via DuckDuckGo ----
    candidates: list[tuple[str, str, dict]] = []   # (segment, url, search_result)
    seen_domains: set[str] = set()

    total_queries = len(queries)
    for i, (segment, q) in enumerate(queries):
        if progress_callback:
            progress_callback(i, total_queries * 2, f"Searching: {segment} — {q}")
        full_query = f"{q} {location}"
        for r in ddg_search(full_query, max_per_query):
            url = r.get("href") or r.get("url") or ""
            if not url:
                continue
            domain = normalize_domain(url)
            if not domain or domain in seen_domains:
                continue
            if is_blacklisted(url, domain_blacklist):
                continue
            seen_domains.add(domain)
            candidates.append((segment, url, r))
        time.sleep(0.6)  # gentle pacing between DDG calls

    # ---- Phase 2: enrich each candidate ----
    leads: list[Lead] = []
    total_candidates = len(candidates)
    for i, (segment, url, ddg_result) in enumerate(candidates):
        step_msg = f"Enriching {normalize_domain(url)}"
        if progress_callback:
            progress_callback(total_queries + i, total_queries + total_candidates, step_msg)

        # Pre-filter against existing partners using just URL + DDG title
        title_guess = ddg_result.get("title", "")
        if matches_existing_partner(url, title_guess, existing_partners):
            lead = Lead(
                company=title_guess[:80],
                segment=segment,
                website=url,
                existing_partner=True,
                status="Disqualified",
                fit_score=1,
                notes="Already an existing partner.",
                specialization=ddg_result.get("body", "")[:200],
            )
            leads.append(lead)
            continue

        info: dict = {
            "company": title_guess[:80],
            "specialization": ddg_result.get("body", "")[:200],
            "address": "",
            "email": "",
            "phone": "",
        }
        if enrich_websites:
            web_info = enrich_from_website(url)
            for k, v in web_info.items():
                if v:
                    info[k] = v

        # Re-check existing partner now that we have the proper company name
        if matches_existing_partner(url, info["company"], existing_partners):
            lead = Lead(
                company=info["company"],
                segment=segment,
                website=url,
                specialization=info["specialization"],
                email=info.get("email", ""),
                phone=info.get("phone", ""),
                address=info.get("address", ""),
                existing_partner=True,
                status="Disqualified",
                fit_score=1,
                notes="Already an existing partner.",
            )
            leads.append(lead)
            continue

        # Geocode if we have an address
        geo: dict = {}
        if info.get("address"):
            if progress_callback:
                progress_callback(total_queries + i, total_queries + total_candidates,
                                  f"Geocoding {info['company']}")
            geo = geocode(info["address"])

        lead = Lead(
            company=info["company"],
            segment=segment,
            website=url,
            address=info.get("address", ""),
            email=info.get("email", ""),
            phone=info.get("phone", ""),
            specialization=info.get("specialization", ""),
            attends_fam=info.get("attends_fam", False),
            city=geo.get("city", ""),
            country=geo.get("country", ""),
            latitude=geo.get("latitude"),
            longitude=geo.get("longitude"),
        )
        lead.status, lead.fit_score = auto_qualify(lead, target_keywords)
        leads.append(lead)

    if progress_callback:
        progress_callback(1, 1, "Done")
    return leads


def leads_to_records(leads: list[Lead]) -> list[dict]:
    return [asdict(l) for l in leads]


def enrich_urls(
    url_records: list[dict],
    target_keywords: list[str] | None = None,
    existing_partners: list[str] | None = None,
    source: str = "competitor",
    progress_callback=None,
) -> list[Lead]:
    """Enrich a pre-discovered list of URLs (from competitor mining or directory scrape).

    url_records: [{"name": ..., "url": ...}, ...]
    Skips DDG search entirely — goes straight to enrichment + qualification.
    """
    target_keywords = target_keywords or []
    existing_partners = existing_partners or []
    leads: list[Lead] = []
    total = len(url_records)

    for i, rec in enumerate(url_records):
        url = rec.get("url", "")
        if not url:
            continue
        if progress_callback:
            progress_callback(i, total, f"Enriching {normalize_domain(url)}")

        # Existing partner pre-check (cheap)
        if matches_existing_partner(url, rec.get("name", ""), existing_partners):
            leads.append(Lead(
                company=rec.get("name", "")[:80],
                website=url,
                source=source,
                existing_partner=True,
                status="Disqualified",
                fit_score=1,
                notes="Already an existing partner.",
            ))
            continue

        web_info = enrich_from_website(url)
        company = web_info.get("company") or rec.get("name", "")[:80]

        if matches_existing_partner(url, company, existing_partners):
            leads.append(Lead(
                company=company,
                website=url,
                source=source,
                specialization=web_info.get("specialization", ""),
                email=web_info.get("email", ""),
                phone=web_info.get("phone", ""),
                address=web_info.get("address", ""),
                existing_partner=True,
                status="Disqualified",
                fit_score=1,
                notes="Already an existing partner.",
            ))
            continue

        geo = geocode(web_info.get("address", "")) if web_info.get("address") else {}

        lead = Lead(
            company=company,
            segment="(via " + source + ")",
            website=url,
            address=web_info.get("address", ""),
            email=web_info.get("email", ""),
            phone=web_info.get("phone", ""),
            specialization=web_info.get("specialization", ""),
            attends_fam=web_info.get("attends_fam", False),
            city=geo.get("city", ""),
            country=geo.get("country", ""),
            latitude=geo.get("latitude"),
            longitude=geo.get("longitude"),
            source=source,
            notes=f"Source: {rec.get('source_page') or rec.get('source') or source}",
        )
        lead.status, lead.fit_score = auto_qualify(lead, target_keywords)
        leads.append(lead)

    if progress_callback:
        progress_callback(1, 1, "Done")
    return leads
