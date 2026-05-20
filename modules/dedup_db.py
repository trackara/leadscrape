"""
modules/dedup_db.py
-------------------
Lightweight SQLite store for past leads. Lets the dashboard:
  - flag returning leads ("we found this one in March's Vienna run")
  - track contact status across searches
  - count how often a domain has been surfaced

Schema is deliberately minimal. Add columns via ALTER TABLE if needed later.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "leads.db"


def _normalize_domain(url: str) -> str:
    if not url:
        return ""
    try:
        netloc = urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


def init_db() -> None:
    """Create the table if it doesn't exist. Safe to call repeatedly."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                domain         TEXT PRIMARY KEY,
                company        TEXT,
                segment        TEXT,
                status         TEXT,
                email          TEXT,
                city           TEXT,
                country        TEXT,
                first_seen     TEXT NOT NULL,
                last_seen      TEXT NOT NULL,
                search_count   INTEGER DEFAULT 1,
                contacted      INTEGER DEFAULT 0,
                contacted_at   TEXT,
                notes          TEXT
            )
        """)
        conn.commit()


def lookup_existing(domains: list[str]) -> dict[str, dict]:
    """Return {domain: row_dict} for domains that exist in the DB."""
    if not domains:
        return {}
    init_db()
    placeholders = ",".join("?" * len(domains))
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"SELECT * FROM leads WHERE domain IN ({placeholders})",
            domains,
        ).fetchall()
    return {row["domain"]: dict(row) for row in rows}


def record_leads(leads: list) -> None:
    """Upsert each lead. Increments search_count on conflict."""
    if not leads:
        return
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as conn:
        for lead in leads:
            domain = _normalize_domain(getattr(lead, "website", ""))
            if not domain:
                continue
            conn.execute("""
                INSERT INTO leads (
                    domain, company, segment, status, email, city, country,
                    first_seen, last_seen, search_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(domain) DO UPDATE SET
                    last_seen    = excluded.last_seen,
                    search_count = leads.search_count + 1,
                    status       = excluded.status,
                    company      = COALESCE(NULLIF(excluded.company, ''), leads.company),
                    email        = COALESCE(NULLIF(excluded.email, ''), leads.email),
                    city         = COALESCE(NULLIF(excluded.city, ''), leads.city),
                    country      = COALESCE(NULLIF(excluded.country, ''), leads.country)
            """, (
                domain,
                getattr(lead, "company", ""),
                getattr(lead, "segment", ""),
                getattr(lead, "status", ""),
                getattr(lead, "email", ""),
                getattr(lead, "city", ""),
                getattr(lead, "country", ""),
                now,
                now,
            ))
        conn.commit()


def annotate_leads_with_history(leads: list) -> list:
    """Mutate each lead in-place: set is_new (bool) and previously_seen (date or None)."""
    domains = [_normalize_domain(getattr(l, "website", "")) for l in leads]
    domains = [d for d in domains if d]
    history = lookup_existing(domains)
    for lead in leads:
        domain = _normalize_domain(getattr(lead, "website", ""))
        if domain in history:
            lead.is_new = False
            lead.previously_seen = history[domain].get("first_seen", "")
        else:
            lead.is_new = True
            lead.previously_seen = ""
    return leads


def all_leads() -> list[dict]:
    """Return every lead in the DB as list of dicts. Used for the History tab."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY last_seen DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def mark_contacted(domain: str, note: str = "") -> None:
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE leads SET contacted = 1, contacted_at = ?, notes = ? WHERE domain = ?",
            (now, note, _normalize_domain(domain) or domain),
        )
        conn.commit()


def delete_lead(domain: str) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM leads WHERE domain = ?",
                     (_normalize_domain(domain) or domain,))
        conn.commit()


def stats() -> dict:
    """Quick rollup for the History tab header."""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        contacted = conn.execute("SELECT COUNT(*) FROM leads WHERE contacted = 1").fetchone()[0]
        qualified = conn.execute(
            "SELECT COUNT(*) FROM leads WHERE status = 'Qualified'"
        ).fetchone()[0]
    return {"total": total, "contacted": contacted, "qualified": qualified}
