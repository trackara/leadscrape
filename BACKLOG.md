# Backlog — parked ideas, not for now

Features Emma has explicitly said "remember for later, not now." Do **not** build these unless she asks.

---

## Decision-maker extraction
**Parked:** 2026-05-04
**Effort:** ~2 hours
**Why it matters:** `info@` emails go to a generic inbox. `firstname.lastname@` with a personalized subject line gets opened. Doubles outreach response rate.

**Implementation sketch:**
- After fetching the homepage in `pipeline.py`, also fetch `/team`, `/about`, `/ueber-uns`, `/people`, `/staff`.
- Parse the HTML for `Name + Role + Email` patterns. Common shapes:
  - `<h3>Maria Schmidt</h3><p>Head of Sales</p><a href="mailto:m.schmidt@...">`
  - vCard markup, `itemtype="Person"` schema.org blocks
  - `<img alt="Maria Schmidt">` near a role string
- Add fields to `Lead`: `contact_name`, `contact_role`, `contact_email`.
- Prioritize roles: Sales / Partnerships / MICE / Director / Founder > generic.
- Dashboard column: "Best contact" showing name + role + direct email.
- Excel export: include both `email` (generic) and `contact_email` (personal).

**Watch out:**
- GDPR — name + role + work email is fine for B2B outreach (legitimate interest), but document the source URL in the lead so you can show provenance if challenged.
- Don't grab personal mobile numbers from team pages even if listed.
