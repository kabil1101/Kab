"""The hand-kept half of the policy radar.

The Federal Register can only know about actions that have already been
signed. It cannot know that a summit is scheduled, that a court will rule in a
given term, or that a deadline was announced in a speech and never published
as a document. Those dates exist only because a person wrote them down, so
this module reads them from `data/watchlist.txt`.

The format is one event per line, pipe-separated, because the person
maintaining it is not a programmer and YAML punishes a misplaced space:

    2026-09-29 | tariff | Section 232 pharma tariff takes effect | https://... | 2026-09-05

A curated file's real failure mode is going stale silently — an entry nobody
has checked for three months reads exactly like one confirmed this morning.
So the fifth field is the date the entry was last verified, and the renderer
marks anything older than STALE_DAYS. A visibly stale entry is recoverable; an
invisibly stale one is what puts a wrong date in front of a trade.

Every parse problem is reported and skipped. One malformed line must not cost
the reader the other twenty, nor the rest of the brief.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

WATCHLIST_PATH = Path(__file__).resolve().parent.parent / "data" / "watchlist.txt"

# Past this age an entry is shown with a warning rather than trusted silently.
# D11, amended 2026-09-18: the confirmation horizon is per class, not one
# number for everything. A holiday entry would flag `unconfirmed` within 75
# days of every refresh, and **a flag that always fires is a flag nobody
# reads.** Policy dates genuinely decay - summits move, court dates slip -
# and statutory ones do not.
STALE_DAYS = 75                      # policy: unchanged, and still the default
CLASS_STALE_DAYS = {
    "policy": 75,
    "statutory": 365,                # fixed in law; it cannot move
    "holiday": 365,                  # announced annually, then fixed
    "unlock": 30,                    # reserved; unlocks dropped, no free source
}

# How many days before an event it starts appearing. Absent means the old
# behaviour: visible across the whole radar horizon. Impact sets lead time,
# so a hand-entered line can ask for a year's notice or a week's.
DEFAULT_LEAD_DAYS = 365

FIELDS = ("date", "tag", "title", "url", "verified")


def _parse_date(raw: str):
    try:
        return date.fromisoformat(raw.strip())
    except ValueError:
        return None


def parse(text: str) -> dict:
    """Split the file into usable events and a list of complaints."""
    events, problems = [], []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            problems.append(f"line {lineno}: needs at least "
                            f"date | tag | event")
            continue
        when = _parse_date(parts[0])
        if when is None:
            problems.append(f"line {lineno}: {parts[0]!r} is not a "
                            f"YYYY-MM-DD date")
            continue
        if not parts[2]:
            problems.append(f"line {lineno}: event text is empty")
            continue
        verified = _parse_date(parts[4]) if len(parts) > 4 and parts[4] else None
        if len(parts) > 4 and parts[4] and verified is None:
            problems.append(f"line {lineno}: verified date {parts[4]!r} "
                            f"is not YYYY-MM-DD")

        # Fields 6 and 7 are optional and new. A five-field line written
        # before they existed parses to exactly what it always did - the file
        # is maintained by hand and a format change that invalidates the
        # existing lines is a format change that loses them.
        klass = (parts[5] or "").lower() if len(parts) > 5 else ""
        if klass and klass not in CLASS_STALE_DAYS:
            problems.append(f"line {lineno}: class {klass!r} is not one of "
                            f"{', '.join(sorted(CLASS_STALE_DAYS))}")
            klass = ""
        lead = DEFAULT_LEAD_DAYS
        if len(parts) > 6 and parts[6]:
            try:
                lead = int(parts[6])
            except ValueError:
                problems.append(f"line {lineno}: lead {parts[6]!r} is not a "
                                f"whole number of days")
            else:
                if lead < 0:
                    problems.append(f"line {lineno}: lead {lead} is negative")
                    lead = DEFAULT_LEAD_DAYS

        events.append({
            "date": when,
            "tag": (parts[1] or "").lower() or "event",
            "title": parts[2],
            "url": (parts[3] or None) if len(parts) > 3 else None,
            "verified": verified,
            "class": klass or "policy",
            "lead": lead,
            "kind": "curated",
        })
    events.sort(key=lambda e: (e["date"], e["title"]))
    return {"events": events, "problems": problems}


def load(path: Path = WATCHLIST_PATH) -> dict:
    """Read the watchlist. A missing file is a valid empty watchlist."""
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        return {"events": [], "problems": []}
    except OSError as exc:
        return {"events": [],
                "problems": [f"{path.name} unreadable: {type(exc).__name__}"]}
    return parse(text)


def is_stale(event, today: date) -> bool:
    """True when nobody has confirmed this entry recently enough to trust.

    The horizon depends on what kind of date it is (D11, amended). A statutory
    date cannot move, so re-confirming it every ten weeks teaches the reader
    to ignore the flag - which costs the flag its meaning on the policy dates
    that genuinely do move.
    """
    verified = event.get("verified")
    if verified is None:
        return True
    horizon = CLASS_STALE_DAYS.get(event.get("class") or "policy", STALE_DAYS)
    return (today - verified).days > horizon


def within_lead(event, today: date) -> bool:
    """Is this entry close enough to start showing?

    A 365-day horizon that prints everything floods, and a section nobody
    reads is worse than no section - the flat-list failure the tier redesign
    exists to fix.
    """
    days = (event["date"] - today).days
    return days <= event.get("lead", DEFAULT_LEAD_DAYS)
