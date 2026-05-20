# Lead Finder — San Canzian

This is the project context file. Any future developer (or AI assistant) working on this codebase should read this first.

---

## About San Canzian

**San Canzian Hotel & Residences** is a 5-star boutique luxury hotel in Mužolini Donji, Istria, Croatia (near Buje). Member of Small Luxury Hotels of the World (SLH).

- **Property today:** 26 rooms, suites and villas in a restored medieval village
- **2026 extension:** +34 fully serviced club villas and residences
- **Restaurant:** Luciano (Michelin-recommended), led by Chef Pavo Klarić
- **Setting:** Olive groves, vineyards, spa, infinity pool
- **Strengths:** Truffle hunting, olive-oil tastings, destination weddings, small corporate events (up to 50 pax)
- **Co-owner:** Leopold Botteri
- **Website:** https://san-canzian.com

## Why this tool exists

San Canzian wants to grow its B2B partner network — tour operators, MICE/incentive agencies, wedding planners, DMCs — that send guests to Istria. The sales team needs a fast way to find qualified candidates in any region without paying for expensive lead-gen platforms (Apollo, Cognism, etc.).

This tool replaces ~80% of that workflow at €0 monthly cost.

## Target partner segments

In rough order of priority:

1. **Luxury tour operators** — FIT, tailor-made, ultra-luxury (e.g. OneFineMoment-tier)
2. **MICE & incentive agencies** — corporate retreats, reward trips, small conferences
3. **Destination wedding planners** — Istria + Mediterranean focus
4. **DMCs** — established Croatia/Adriatic operators
5. **Boutique tour operators** — culinary, wine, wellness niche

## Geographic priority

1. **DACH** (Germany, Austria, Switzerland) — primary, source markets for luxury Croatia travel
2. **UK** — high-spend luxury segment
3. **Italy** — neighboring, MICE potential
4. **Nordics & Benelux** — emerging luxury demand
5. **North America** — luxury FIT, longer-term

## Each lead must include

These are the required fields. The pipeline must populate all of them or flag them as missing.

| Field | Description |
|---|---|
| `company` | Company name |
| `address`, `city`, `country` | Exact location |
| `latitude`, `longitude` | Coordinates (geocoded) |
| `website` | Company URL |
| `email` | Direct contact email |
| `phone` | Phone number |
| `specialization` | One-sentence relevance summary |
| `status` | Qualified / Needs Review / Disqualified |
| `existing_partner` | Boolean — must be `False` to appear in default results |

## Existing partners (default exclusion list)

These already work with San Canzian and should NOT appear as new leads. They live in `config.py` → `EXISTING_PARTNERS` and can be edited by the sales team via the dashboard sidebar.

- Small Luxury Hotels of the World (SLH) — `slh.com`
- Mr & Mrs Smith — `mrandmrssmith.com`
- Sovereign Luxury Travel — `sovereign.com`
- Classic Travel (Virtuoso member) — `classictravel.com`
- The Luxe Voyager — `theluxevoyager.com`
- Hilton SLH partnership — `hilton.com`

## Tech stack

All free, no paid APIs.

- **Discovery:** DuckDuckGo Search (`duckduckgo-search` Python package, no API key)
- **Geocoding:** OpenStreetMap Nominatim (no API key, 1 req/sec rate limit)
- **Scraping:** `requests` + `BeautifulSoup`
- **UI:** Streamlit
- **Export:** `openpyxl`

## Project layout

```
lead_finder/
├── CLAUDE.md          # This file
├── README.md          # User-facing setup guide
├── app.py             # Streamlit dashboard
├── pipeline.py        # Search → scrape → enrich → qualify
├── config.py          # Segments, languages, partner exclusion list
├── requirements.txt
└── .env.example
```

## How to extend

- **New segment** → edit `SEGMENT_QUERIES` in `config.py`
- **New language** → add translated keywords to each segment's query list
- **New partner to exclude** → either edit `EXISTING_PARTNERS` in `config.py` or paste in dashboard sidebar
- **Better qualification** → tune `auto_qualify` in `pipeline.py` (keyword-based, transparent on purpose)

## Known limitations

- DuckDuckGo can rate-limit aggressive runs — keep searches under ~5 segments at once
- OSM Nominatim has spotty coverage for very small businesses
- Website scraping fails on JavaScript-only sites (rare for travel agencies)
- No CRM integration yet — Excel export only

## Parked — see BACKLOG.md

Features Emma has explicitly deferred. Read `BACKLOG.md` before suggesting "new" ideas — they may already be queued. Don't build any of them unless asked.

## Out of scope

- Outbound email automation (use a separate tool — Lemlist, Instantly, etc.)
- LinkedIn scraping (ToS violation, do not add)
- Personal contact enrichment (GDPR risk, use B2B role-based emails only)
