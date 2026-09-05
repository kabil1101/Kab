"""Day-over-day memory.

Every brief before this one was stateless, so no figure carried a comparison —
"BTC $79,670" with nothing to say whether that was a jump or a drift. This
module keeps one small JSON file, committed back to the repo after each
successful send, holding the handful of numbers worth comparing against
tomorrow.

Three things fall out of that one file:

  - Real day-over-day deltas. Kraken's ticker carries no 24h-ago price, so
    until now the honest best was where price sat in its 24h range.
  - The "already sent today" marker. GitHub fires the scheduled run hours
    late; once an external trigger is sending the brief on time, a late
    scheduled run must not follow it with a second, staler copy.
  - Repo activity. GitHub disables scheduled workflows in repositories with no
    commits for 60 days, and a daily state commit keeps that clock reset.

Every read is tolerant. A missing file is the normal first run; a corrupt one
is a bug somewhere else and must still not cost the reader their email, so
both degrade to "no previous state" rather than raising.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "state" / "latest.json"

# Only figures whose day-over-day move is genuinely new information. Deltas are
# deliberately NOT kept for the cross-asset block: Yahoo already returns a
# change against the previous close, and a second, differently-derived "vs
# yesterday" beside it would invite the reader to trust two numbers that
# measure subtly different things.
TRACKED = ("btc", "eth", "sol", "fng")


def load(path: Path = STATE_PATH) -> dict:
    """Previous run's snapshot, or {} if there isn't a usable one."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as exc:
        # A corrupt state file is someone else's bug. It costs the deltas; it
        # must never cost the email.
        print(f"::warning::state file unreadable ({type(exc).__name__}); "
              f"continuing without day-over-day deltas", file=sys.stderr)
        return {}
    return data if isinstance(data, dict) else {}


def snapshot(ctx, sent_on: date | None = None) -> dict:
    """Reduce a run's context to the few numbers tomorrow will want."""
    snap: dict = {"date": ctx["now"].date().isoformat()}
    if sent_on is not None:
        snap["last_sent_date"] = sent_on.isoformat()

    c = ctx.get("crypto")
    if c and c["ok"]:
        for p in c["data"]["pairs"]:
            key = p["symbol"].lower()
            if key in TRACKED:
                snap[key] = p["last"]

    f = ctx.get("fear_greed")
    if f and f["ok"]:
        snap["fng"] = f["data"]["today"]["value"]

    return snap


def save(snap: dict, path: Path = STATE_PATH) -> None:
    """Write the snapshot. Raises; the caller decides whether that matters."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2, sort_keys=True)
        fh.write("\n")


def already_sent_today(prev: dict, today: date) -> bool:
    """True if a brief for `today` has already gone out.

    The scheduled run is a fallback behind an external trigger that fires on
    time. Without this check a schedule delayed by four hours would deliver a
    second copy of a brief the reader already has, with staler numbers.
    """
    return prev.get("last_sent_date") == today.isoformat()


def delta(prev: dict, key: str, current):
    """(absolute, percent) move since the last run, or None if not comparable."""
    if current is None:
        return None
    was = prev.get(key)
    if not isinstance(was, (int, float)) or was == 0:
        return None
    return current - was, (current - was) / was * 100.0
