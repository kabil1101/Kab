"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.

Round 23 — can anything free carry a FORWARD release schedule?
==============================================================

Addendum 2's Addition D, Phase 1: Kabil wants the dates of CPI, PPI, the
Employment Situation and GDP far enough ahead to plan around. His words - *"i
have to be aware of the dates at every start of the month so i have plenty of
time to plan my moves."*

**Step 1 of the addendum's source order is already answered, and the answer is
no.** It asks whether the wired calendar reaches a month out. It does not:
`FF_THIS_WEEK` is the only ForexFactory feed, `ff_calendar_nextweek.json` was
probed against a runner and 404s, and `calendar()` returns `week_only: True`.
The brief is not truncating a longer source to five sessions - the source stops
on Friday. So this round starts at Step 2.

Three questions per target, the same three every feed has answered:

  - does it answer 200 from a runner
  - how far FORWARD does it actually reach
  - does it distinguish a SCHEDULED date from a RELEASED one

The third is the one specific to this addition, and it is the whole risk. A
date on a calendar is a plan: releases slip, for shutdowns and for revisions
to the publication schedule. A line that prints only the scheduled date
asserts something that may not have happened - which is D25's problem in a
different costume, and needs the same three states rather than two.

§12.10 stands and is not reopened: FRED's release-dates endpoint must not be
used to decide whether something HAS published. Asking it for *forward
scheduled* dates is a different claim about a different route, and §12.4a says
a verdict does not transfer. It needs its own entry either way.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402  - for its real headers, not its fetchers

TIMEOUT = 25
NOW = datetime.now(timezone.utc)
OKX = "https://www.okx.com/api/v5/public/liquidation-orders"


def _get(url, params=None, headers=None, note=""):
    print(f"    {url}")
    if note:
        print(f"    ({note})")
    try:
        r = requests.get(url, params=params, timeout=TIMEOUT,
                         headers=headers or sources.HEADERS)
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED {type(exc).__name__}: {str(exc)[:120]}")
        return None
    print(f"    HTTP {r.status_code} · {len(r.content):,} bytes")
    if r.status_code != 200:
        print(f"    body: {r.text[:160]}")
        return None
    try:
        return r.json()
    except Exception:  # noqa: BLE001
        print(f"    not JSON: {r.text[:160]}")
        return None


def _rows(payload):
    """Flatten OKX's per-instrument `details` into one list."""
    out = []
    for block in (payload or {}).get("data") or []:
        for d in block.get("details") or []:
            d = dict(d)
            d["instId"] = block.get("instId") or block.get("uly")
            out.append(d)
    return out


def _span(rows):
    if not rows:
        return None
    ts = sorted(int(r["ts"]) for r in rows if r.get("ts"))
    if not ts:
        return None
    newest = datetime.fromtimestamp(ts[-1] / 1000, timezone.utc)
    oldest = datetime.fromtimestamp(ts[0] / 1000, timezone.utc)
    return newest, oldest, (newest - oldest).total_seconds() / 3600


def head(n, title, why):
    print(f"\n=== {n}. {title}\n    WHY: {why}")



FRED_RELEASES = "https://api.stlouisfed.org/fred/releases"
FRED_RELEASES_DATES = "https://api.stlouisfed.org/fred/releases/dates"
FRED_RELEASE_DATES = "https://api.stlouisfed.org/fred/release/dates"

# What Kabil named, and the release each actually belongs to. NFP is one number
# inside the Employment Situation - the same release BACKDROP already reads the
# unemployment rate from. One release, two sections.
WANTED = ("Consumer Price Index", "Producer Price Index",
          "Employment Situation", "Gross Domestic Product")

# Phase 1 needs the next release of each, and enough runway to plan. A source
# that reaches two weeks is no better than the ForexFactory feed.
FORWARD_PASS_DAYS = 60

AGENCY_TARGETS = (
    ("BLS .ics schedule", "https://www.bls.gov/schedule/news_release/bls.ics"),
    ("BLS schedule page", "https://www.bls.gov/schedule/news_release/2026_sched.htm"),
    ("BLS news RSS", "https://www.bls.gov/feed/bls_news.rss"),
    ("BEA news RSS", "https://www.bea.gov/rss.xml"),
    ("BEA release schedule", "https://www.bea.gov/news/schedule"),
)


def _fred(url, key, params, note=""):
    """A FRED call that never echoes the key into the log."""
    print(f"    {url}")
    if note:
        print(f"    ({note})")
    try:
        r = requests.get(url, params=dict(params, api_key=key,
                                          file_type="json"),
                         timeout=TIMEOUT, headers=sources.HEADERS)
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED {type(exc).__name__}: {str(exc)[:110]}")
        return None
    print(f"    HTTP {r.status_code} · {len(r.content):,} bytes")
    if r.status_code != 200:
        body = " ".join(r.text.split())[:200].replace(key, "***")
        print(f"    body: {body}")
        return None
    return r.json()


def main() -> int:
    key = (os.environ.get("FRED_API_KEY") or "").strip()
    today = NOW.date()
    rows = []

    # ---- 1. does FRED publish forward scheduled dates at all? ----------
    head(1, "FRED — forward release dates across all releases",
         "`include_release_dates_with_no_data=true` is the flag that should "
         "surface a date with nothing published against it yet. That is "
         "exactly the scheduled-not-released distinction this needs.")
    if not key:
        print("    FRED_API_KEY is not set; skipping targets 1-3.")
    else:
        d = _fred(FRED_RELEASES_DATES, key, {
            "realtime_start": today.isoformat(),
            "include_release_dates_with_no_data": "true",
            "sort_order": "asc", "limit": "200"})
        if d:
            dates = d.get("release_dates") or []
            print(f"    rows {len(dates)} · keys "
                  f"{sorted(dates[0].keys()) if dates else '-'}")
            ahead = [r for r in dates
                     if r.get("date", "") > today.isoformat()]
            print(f"    rows dated AFTER today: {len(ahead)}")
            if ahead:
                far = max(r["date"] for r in ahead)
                reach = (date.fromisoformat(far) - today).days
                print(f"    furthest forward: {far} ({reach}d out)")
                for r in ahead[:6]:
                    print(f"      · {r.get('date')}  "
                          f"{str(r.get('release_name'))[:58]}")
                rows.append(("FRED releases/dates",
                             "PASS" if reach >= FORWARD_PASS_DAYS else "THIN",
                             f"{reach}d, {len(ahead)} rows"))
            else:
                print("    NOTHING dated after today - cannot carry a forward "
                      "date")
                rows.append(("FRED releases/dates", "FAIL", "no forward rows"))

    # ---- 2. the four releases by id ------------------------------------
    head(2, "FRED — the four releases Kabil named, by release id",
         "Discovered by name rather than hardcoded. A guessed id is a guessed "
         "verdict.")
    ids = {}
    if key:
        d = _fred(FRED_RELEASES, key, {"limit": "1000"},
                  note="to resolve names to ids")
        for rel in (d or {}).get("releases") or []:
            name = str(rel.get("name") or "")
            for want in WANTED:
                if name.strip().lower() == want.lower():
                    ids[want] = rel.get("id")
        print(f"    resolved: {ids}")
        for want in WANTED:
            rid = ids.get(want)
            if rid is None:
                print(f"\n    {want}: NO EXACT NAME MATCH - needs a look at "
                      f"the release list by hand")
                rows.append((want[:19], "FAIL", "no id matched"))
                continue
            print(f"\n    --- {want} (id {rid}) ---")
            dd = _fred(FRED_RELEASE_DATES, key, {
                "release_id": str(rid),
                "realtime_start": today.isoformat(),
                "include_release_dates_with_no_data": "true",
                "sort_order": "asc", "limit": "40"})
            got = [r.get("date") for r in (dd or {}).get("release_dates") or []]
            ahead = [g for g in got if g and g > today.isoformat()]
            if not ahead:
                print(f"    no forward dates (got {len(got)} rows, all past)")
                rows.append((want[:19], "FAIL", "no forward dates"))
                continue
            reach = (date.fromisoformat(max(ahead)) - today).days
            print(f"    next {ahead[0]} · {len(ahead)} forward · "
                  f"furthest {max(ahead)} ({reach}d)")
            rows.append((want[:19],
                         "PASS" if reach >= FORWARD_PASS_DAYS else "THIN",
                         f"next {ahead[0]}, {reach}d"))

    # ---- 3. scheduled vs released, which is the whole risk --------------
    head(3, "Does FRED tell a SCHEDULED date from a RELEASED one?",
         "If every row looks identical whether or not the number exists, the "
         "brief cannot say 'the date passed and nothing printed' - and will "
         "count down past a release that slipped. Three states, not two.")
    if key and ids.get("Consumer Price Index"):
        rid = ids["Consumer Price Index"]
        with_nd = _fred(FRED_RELEASE_DATES, key, {
            "release_id": str(rid), "realtime_start": today.isoformat(),
            "include_release_dates_with_no_data": "true",
            "sort_order": "asc", "limit": "40"},
            note="WITH dates that have no data")
        without = _fred(FRED_RELEASE_DATES, key, {
            "release_id": str(rid), "realtime_start": today.isoformat(),
            "include_release_dates_with_no_data": "false",
            "sort_order": "asc", "limit": "40"},
            note="WITHOUT them")
        a = {r.get("date") for r in (with_nd or {}).get("release_dates") or []}
        b = {r.get("date") for r in (without or {}).get("release_dates") or []}
        only_scheduled = sorted(a - b)
        print(f"    with-no-data rows {len(a)} · with-data-only rows {len(b)}")
        print(f"    dates present ONLY in the first set: {only_scheduled[:8]}")
        if only_scheduled:
            print("    -> the two sets DIFFER, so scheduled is distinguishable "
                  "from released. This is the mechanism Phase 1 needs.")
            rows.append(("scheduled vs released", "PASS",
                         f"{len(only_scheduled)} scheduled-only"))
        else:
            print("    -> the sets are IDENTICAL. FRED cannot tell the brief "
                  "whether a date has published, and the three-state rule "
                  "needs a different source for its third state.")
            rows.append(("scheduled vs released", "FAIL", "sets identical"))

    # ---- 4. the primary sources ----------------------------------------
    head(4, "BLS and BEA — the agencies that own these dates",
         "Whoever else carries them got them from here. Government hosts did "
         "NOT block the runner in the nine-target round, which lowers the odds "
         "of an S1 without removing them.")
    for label, url in AGENCY_TARGETS:
        print(f"\n    --- {label} ---")
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=sources.HEADERS)
            ctype = r.headers.get("content-type", "?")[:40]
            print(f"    {url}")
            print(f"    HTTP {r.status_code} · {len(r.content):,} bytes · {ctype}")
            if r.status_code != 200:
                rows.append((label, "FAIL", f"HTTP {r.status_code}"))
                continue
            text = r.text
            # Cheap shape read: how many future-looking dates can be seen at
            # all. Not a parser - just whether the dates are in there.
            import re as _re
            iso = sorted(set(_re.findall(r"20\d{2}-\d{2}-\d{2}", text)))
            ics = sorted(set(_re.findall(r"DTSTART[^:]*:(20\d{6})", text)))
            fwd = [d for d in iso if d > today.isoformat()]
            fwd_ics = [d for d in ics if d > today.strftime("%Y%m%d")]
            print(f"    ISO dates {len(iso)} ({len(fwd)} forward) · "
                  f"ICS DTSTART {len(ics)} ({len(fwd_ics)} forward)")
            for name in ("Consumer Price Index", "Employment Situation",
                         "Producer Price Index", "Gross Domestic Product"):
                if name.lower() in text.lower():
                    print(f"      mentions {name}")
            best = fwd_ics or fwd
            if best:
                unit = "%Y%m%d" if fwd_ics else "%Y-%m-%d"
                reach = (datetime.strptime(max(best), unit).date()
                         - today).days
                print(f"    furthest forward: {max(best)} ({reach}d out)")
                rows.append((label,
                             "PASS" if reach >= FORWARD_PASS_DAYS else "THIN",
                             f"{reach}d forward"))
            else:
                print("    no forward dates visible in the payload")
                rows.append((label, "FAIL", "no forward dates"))
        except Exception as exc:  # noqa: BLE001
            print(f"    FAILED {type(exc).__name__}: {str(exc)[:110]}")
            rows.append((label, "FAIL", type(exc).__name__))

    print("\n" + "=" * 72)
    print(f"{'TARGET':<26}{'VERDICT':<9}DETAIL")
    print("=" * 72)
    for label, verdict, why in rows:
        print(f"{label:<26}{verdict:<9}{why}")
    print()
    print(f"PASS needs {FORWARD_PASS_DAYS}d of forward reach. THIN means it")
    print("answers but not far enough to plan a month around, which is the")
    print("whole point of the addition.")
    print()
    print("Stop at the first PASS that also clears target 3. A source that")
    print("cannot tell scheduled from released fails the rule before it is")
    print("written, however far forward it reaches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
