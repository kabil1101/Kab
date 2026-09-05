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
STALE_DAYS = 75

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
        events.append({
            "date": when,
            "tag": (parts[1] or "").lower() or "event",
            "title": parts[2],
            "url": (parts[3] or None) if len(parts) > 3 else None,
            "verified": verified,
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
    """True when nobody has confirmed this entry recently enough to trust."""
    verified = event.get("verified")
    if verified is None:
        return True
    return (today - verified).days > STALE_DAYS
