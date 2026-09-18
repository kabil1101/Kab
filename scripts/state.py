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

# The state bundle. One schema change carrying several features, because
# shipping a schema change alone for a feature that produces nothing for a
# month is the wrong trade - and shipping two schema changes is worse.
#
# Everything below degrades to silence on an old state file. A brief written
# before these keys existed simply has none of them, which yields no claim
# rather than a wrong one.
HISTORY_DAYS = 30

# Figures worth a 30-day series. Each one is here because a specific line
# needs it, not because it was available:
#   btc/eth/sol   range position over 7 and 30 days, and days-since counters
#   fng           unchanged, day-over-day
#   btc_dom       dominance moves slowly; a day delta on it is noise, a week
#                 is not
#   stable_supply D24's supply leg, week-over-week
#   oi_btc        open interest CHANGE against price change - a level says
#                 nothing, the pair is the positioning read (addendum A)
#   vol_btc       today's volume against its own 30-day average
SERIES_KEYS = ("btc", "eth", "sol", "fng", "btc_dom", "stable_supply",
               "oi_btc", "vol_btc")


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


def _figures(ctx) -> dict:
    """Every tracked number this run produced, by key."""
    out: dict = {}
    c = ctx.get("crypto")
    if c and c["ok"]:
        for p in c["data"]["pairs"]:
            key = p["symbol"].lower()
            if key in TRACKED:
                out[key] = p["last"]
            # Kraken calls it vol_24h. Getting this name wrong stores
            # nothing and fails silently, which is why the test below asserts
            # the value rather than the presence of the key.
            if key == "btc" and p.get("vol_24h") is not None:
                out["vol_btc"] = p["vol_24h"]

    f = ctx.get("fear_greed")
    if f and f["ok"]:
        out["fng"] = f["data"]["today"]["value"]

    g = ctx.get("global_mcap")
    if g and g["ok"]:
        if g["data"].get("btc_dominance") is not None:
            out["btc_dom"] = g["data"]["btc_dominance"]
        if g["data"].get("stable_supply_usd") is not None:
            out["stable_supply"] = g["data"]["stable_supply_usd"]

    p_ = ctx.get("perp_btc")
    if p_ and p_["ok"] and p_["data"].get("open_interest") is not None:
        out["oi_btc"] = p_["data"]["open_interest"]
    return out


def snapshot(ctx, sent_on: date | None = None, prev: dict | None = None) -> dict:
    """Reduce a run's context to the numbers later runs will want.

    Written by the MORNING edition only. The PM edition is read-only against
    everything here except its own send marker - if it overwrote the daily
    baseline, tomorrow's "vs yesterday" would compare 09:20 against 14:00
    yesterday, a nineteen-hour move labelled as a daily one. That is §3.18
    exactly, and it cost a correction once already.
    """
    today = ctx["now"].date()
    snap: dict = {"date": today.isoformat()}
    if sent_on is not None:
        snap["last_sent_date"] = sent_on.isoformat()
    snap.update(_figures(ctx))

    # Carry the PM marker across untouched: it belongs to the other edition
    # and the AM run has no business resetting it.
    if prev and prev.get("last_sent_pm_date"):
        snap["last_sent_pm_date"] = prev["last_sent_pm_date"]

    # The PM baseline. Same numbers, kept separately, so the PM edition can
    # say "since the 09:20 brief" and mean it.
    snap["am"] = dict(snap.get("am") or {}, **_figures(ctx),
                      **{"at": ctx["now"].isoformat()})

    # A 30-day rolling series, newest last, one entry per calendar day. A
    # second run on the same day replaces that day rather than appending, so a
    # manual re-send does not distort an average.
    history = [h for h in (prev or {}).get("history") or []
               if isinstance(h, dict) and h.get("date") != today.isoformat()]
    history.append(dict(_figures(ctx), date=today.isoformat()))
    snap["history"] = history[-HISTORY_DAYS:]
    return snap


def pm_mark(prev: dict, sent_on: date) -> dict:
    """The PM edition's only write: that it sent.

    Everything else in the file belongs to the morning. Returned as a new dict
    rather than mutated, so a caller cannot half-apply it.
    """
    return dict(prev or {}, last_sent_pm_date=sent_on.isoformat())


def series(prev: dict, key: str) -> list:
    """The stored history for one figure, oldest first. [] when unknown."""
    out = []
    for row in (prev or {}).get("history") or []:
        if isinstance(row, dict) and isinstance(row.get(key), (int, float)):
            out.append(row[key])
    return out


def average(prev: dict, key: str, days: int = HISTORY_DAYS):
    """Mean of the last `days` stored values, or None if too few to mean it."""
    vals = series(prev, key)[-days:]
    # Two points is not an average. A number that pretends to be one for the
    # first month after shipping is worse than no number, because nobody would
    # know to distrust it.
    if len(vals) < 5:
        return None
    return sum(vals) / len(vals)


def range_position(prev: dict, key: str, current, days: int):
    """Where `current` sits in the last `days` of stored values, 0-100.

    None when the window is short or flat. A flat window has no position in
    it, and dividing by its zero width would invent one.
    """
    if current is None:
        return None
    vals = series(prev, key)[-days:]
    if len(vals) < max(3, days // 4):
        return None
    lo, hi = min(vals + [current]), max(vals + [current])
    if hi == lo:
        return None
    return (current - lo) / (hi - lo) * 100.0


def days_since(prev: dict, key: str, test) -> int | None:
    """Sessions since `test` was last true of a stored value.

    0 means today. None means it is not in the window at all - which is a
    different statement from "a long time ago" and must not be printed as one.
    """
    vals = series(prev, key)
    for back, v in enumerate(reversed(vals)):
        try:
            if test(v):
                return back
        except Exception:  # noqa: BLE001 - a bad predicate is not a data claim
            return None
    return None


def am_baseline(prev: dict) -> dict:
    """This morning's figures, for the PM edition. {} when there is none."""
    am = (prev or {}).get("am")
    return am if isinstance(am, dict) else {}


def save(snap: dict, path: Path = STATE_PATH) -> None:
    """Write the snapshot. Raises; the caller decides whether that matters."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2, sort_keys=True)
        fh.write("\n")


def already_sent_pm_today(prev: dict, today: date) -> bool:
    """True if the PM edition has already gone out today.

    Its own marker, checked only by the PM slot. The morning's marker cannot
    serve here: by the time the PM runs, `last_sent_date` is today for the
    ordinary reason that the morning brief was sent, and a shared guard would
    suppress the PM edition every single day.
    """
    return (prev or {}).get("last_sent_pm_date") == today.isoformat()


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
