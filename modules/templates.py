"""
modules/templates.py
--------------------
Outreach email template library.

Templates live as plain Markdown files at:
    data/templates/{language}/{segment_slug}.md

Format:
    ---
    subject: Your subject line
    ---
    Body text with {placeholders}.

Supported placeholders (filled from a Lead):
    {company}           — company name
    {city}              — city
    {country}           — country
    {specialization}    — one-sentence specialization
    {sender_name}       — pulled from config.SENDER (override per render call)
    {sender_role}
    {hotel_name}        — "San Canzian Hotel & Residences" by default
"""

from __future__ import annotations

import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "data" / "templates"

# Map segment label → safe filename slug
SEGMENT_TO_SLUG = {
    "Luxury Tour Operator":     "luxury_tour_operator",
    "MICE Agency":              "mice_agency",
    "Incentive Agency":         "incentive_agency",
    "FIT Tour Operator":        "fit_tour_operator",
    "DMC":                      "dmc",
    "Wedding Planner":          "wedding_planner",
    "Boutique Tour Operator":   "boutique_tour_operator",
    "Corporate Event Planner":  "corporate_event_planner",
}


def list_templates(language: str) -> list[str]:
    """Return list of segment labels that have a template in the given language."""
    lang_dir = TEMPLATES_DIR / language
    if not lang_dir.exists():
        return []
    available_slugs = {p.stem for p in lang_dir.glob("*.md")}
    return [seg for seg, slug in SEGMENT_TO_SLUG.items() if slug in available_slugs]


def load_template(language: str, segment: str) -> dict:
    """Read a template file. Returns {"subject": ..., "body": ...}."""
    slug = SEGMENT_TO_SLUG.get(segment)
    if not slug:
        return {"subject": "", "body": "", "exists": False}
    path = TEMPLATES_DIR / language / f"{slug}.md"
    if not path.exists():
        return {"subject": "", "body": "", "exists": False}

    text = path.read_text(encoding="utf-8")
    subject = ""
    body = text

    # Parse simple frontmatter:   ---\nkey: value\n---\nbody
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, flags=re.DOTALL)
    if m:
        frontmatter, body = m.group(1), m.group(2)
        for line in frontmatter.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                if k.strip().lower() == "subject":
                    subject = v.strip()

    return {"subject": subject, "body": body.strip(), "exists": True}


def save_template(language: str, segment: str, subject: str, body: str) -> Path:
    """Write a template back to disk. Creates the language directory if needed."""
    slug = SEGMENT_TO_SLUG.get(segment)
    if not slug:
        raise ValueError(f"Unknown segment: {segment}")
    lang_dir = TEMPLATES_DIR / language
    lang_dir.mkdir(parents=True, exist_ok=True)
    path = lang_dir / f"{slug}.md"
    text = f"---\nsubject: {subject}\n---\n{body.strip()}\n"
    path.write_text(text, encoding="utf-8")
    return path


def render(template: dict, lead: dict, sender: dict | None = None) -> dict:
    """Substitute placeholders in subject + body."""
    sender = sender or {}
    fields = {
        "company":         lead.get("company", "[company]"),
        "city":            lead.get("city", "[city]"),
        "country":         lead.get("country", "[country]"),
        "specialization":  lead.get("specialization", ""),
        "sender_name":     sender.get("name", "[your name]"),
        "sender_role":     sender.get("role", "[your role]"),
        "hotel_name":      sender.get("hotel_name", "San Canzian Hotel & Residences"),
    }

    def safe_format(s: str) -> str:
        # Replace placeholders without breaking on stray curly braces
        for k, v in fields.items():
            s = s.replace("{" + k + "}", str(v))
        return s

    return {
        "subject": safe_format(template.get("subject", "")),
        "body":    safe_format(template.get("body", "")),
    }
