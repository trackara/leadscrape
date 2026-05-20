# Lead Finder — San Canzian

Internal sales tool. Finds B2B partner candidates anywhere in the world. **No API keys, no costs.**

> Read `CLAUDE.md` first if you're a developer extending this tool — it explains who San Canzian is and what counts as a good lead.

---

## What it does

1. You type a region (e.g. *"Vienna, Austria"*) and pick segments (Luxury Tour Operator, MICE Agency, etc.).
2. Searches DuckDuckGo in multiple languages (EN, DE, FR, IT) for each segment.
3. For every result, visits the company website and pulls: company name, address, email, phone, one-sentence description.
4. Geocodes the address via OpenStreetMap (lat/lng + city/country).
5. Auto-tags each lead **Qualified / Needs Review / Disqualified** based on your keywords.
6. Filters out companies in your **existing partners** list.
7. You filter, review, export to Excel.

---

## Setup (10 minutes, one-time)

### 1. Install Python 3.10+
- macOS: `brew install python` or download from [python.org](https://www.python.org/downloads/)
- Windows: [python.org](https://www.python.org/downloads/) — check "Add Python to PATH"

### 2. Install the tool

```bash
cd lead_finder
python -m venv venv

# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run it

```bash
streamlit run app.py
```

Browser opens at http://localhost:8501. That's the dashboard.

---

## Daily use

1. **Pick language** (English / Hrvatski) in the top-left sidebar.
2. **Type a region** — be specific. *"Vienna, Austria"* works better than *"Austria"*.
3. **Pick segments** to search.
4. **Edit existing partners** in the sidebar if needed (defaults already cover SLH, Mr & Mrs Smith, Sovereign, Classic Travel, Hilton SLH, etc.).
5. Click **Run search**. Wait 1–3 minutes.
6. Filter the table, then click **Download Excel**.

---

## Cost: €0

- **DuckDuckGo Search** — free, no API key, no rate limits for normal use
- **OpenStreetMap Nominatim** (geocoding) — free, 1 request/second (handled automatically)
- **Website scraping** — free
- **Streamlit** — free, runs on your laptop

No bills. No credit cards. No quotas.

---

## Trade-offs vs. paid services

| | This tool (free) | Apollo / Cognism / Google Places |
|---|---|---|
| Cost | €0 | €50–500/month |
| Coverage | Companies with a public website | Larger database, includes "dark" companies |
| Email accuracy | ~60–75% | ~85–95% (verified) |
| Speed | 1–3 min per search | Instant |
| Decision-maker names | No | Yes |

**Honest take:** for a hotel doing weekly searches against well-targeted segments, free is enough. If you ever scale to thousands of leads/month or need verified emails, upgrade to Apollo.

---

## How qualification works

Edit "Qualification keywords" in the sidebar. Words found in a lead's name or description boost its fit score:

- 2+ keywords matched → **Qualified, 5⭐**
- 1 keyword matched → **Qualified, 4⭐**
- Has email/phone but no keyword match → **Needs Review, 3⭐**
- Anti-target words (cruise, youth tour, inbound, etc.) → **Disqualified**

The defaults are tuned for San Canzian (luxury, boutique, Mediterranean, MICE, etc.). Edit per campaign.

---

## Existing-partner exclusion

The "Existing partners" sidebar box accepts:
- **Domains** — `slh.com`, `mrandmrssmith.com`
- **Company name fragments** — `Small Luxury Hotels`, `Sovereign`

Matched leads are auto-tagged `existing_partner=True` and hidden from the default view. Toggle "Include existing partners" to see them.

---

## Extending the tool

| Want to... | Edit |
|---|---|
| Add a new segment | `config.py` → `SEGMENT_QUERIES` |
| Add a search language | `config.py` → add keywords to each segment |
| Change qualification logic | `pipeline.py` → `auto_qualify()` |
| Add UI translations | `config.py` → `UI_STRINGS` |
| Better one-sentence summaries (paid) | Wire an LLM call into `extract_specialization()` in `pipeline.py` |

---

## Troubleshooting

- **"Empty results"** → DuckDuckGo occasionally rate-limits. Wait 30 seconds, retry.
- **Lots of "Needs Review" with no email** → that website doesn't expose direct emails (uses contact forms). Phone usually still comes through.
- **Geocoding wrong city** → the website's address parser found a wrong line. Manually verify in the Excel.
- **Streamlit won't start** → make sure venv is activated. Re-run `pip install -r requirements.txt`.

---

## Legal

- B2B contact data from public business websites is permitted under GDPR (legitimate interest).
- Always include an opt-out in outbound emails.
- Do **not** scrape personal profiles (LinkedIn, Xing, Facebook).
- Honor robots.txt — the scraper already includes polite delays.
