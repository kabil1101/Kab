"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json,*/*;q=0.8",
    # Round 15 saw two calls seconds apart disagree about what "today" was.
    # If an edge cache is in play, say so at the door rather than guessing.
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Round 16. Round 15 established FRED can return a first print together with
# its publication date, which is what the 14:00 edition needs. It left two
# things unresolved, and each of them would put a WRONG DATE in front of a
# reader - the failure this project cares about most.
#
#   Q1  realtime_start came back 2026-09-11 on one call and 2026-09-15 on
#       another seconds later, neither request naming a date. If a cached
#       response can carry a stale "today", that field cannot decide whether
#       something published this morning.
#
#       The resolution is not to trust the default at all. Ask explicitly for
#       today's vintage and check FRED honours it. Then the default's
#       behaviour stops mattering, and Q1 becomes "does an explicit window
#       work" rather than "is the cache lying".
#
#   Q2  releases/dates listed an FOMC press release dated 15 Sep when the
#       decision is on the 16th. If a listed date can mean SCHEDULED rather
#       than PUBLISHED, then "released this morning" cannot rest on it.
#       Decisive test: ask for dates in the FUTURE. Anything returned is by
#       definition not yet published.
#
# And the end-to-end question neither round has asked: given a real release
# that landed this morning, can the brief find it and read its first print?
# The Empire State Manufacturing Survey published today at 08:30 ET, so it is
# the live test case rather than a hypothetical one.
FRED = "https://api.stlouisfed.org/fred"
KEY = (os.environ.get("FRED_API_KEY") or "").strip()

TODAY = date.today().isoformat()
FUTURE = (date.today() + timedelta(days=120)).isoformat()
EMPIRE_STATE_RELEASE = 321     # published this morning per round 15's listing
FOMC_RELEASE = 101             # the one that looked scheduled, not published


def _redact(url: str) -> str:
    return url.replace(KEY, "***REDACTED***") if KEY else url


def _get(label, url, note="", cap=1200):
    print(f"--- {label}\n    {_redact(url)}")
    if note:
        print(f"    ({note})")
    try:
        r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED {type(exc).__name__}: "
              f"{_redact(' '.join(str(exc).split())[:120])}\n")
        return None
    age = r.headers.get("age") or r.headers.get("x-cache") or "-"
    print(f"  HTTP {r.status_code} · {len(r.content):,} bytes · cache hints: {age}")
    data = None
    if "json" in (r.headers.get("content-type") or "").lower():
        try:
            data = json.loads(r.text)
        except json.JSONDecodeError:
            print("  declared JSON, did not parse")
    print(f"  {_redact(' '.join((json.dumps(data) if data is not None else r.text)[:cap].split()))}")
    print()
    return data


def main() -> int:
    if not KEY:
        print("::error::FRED_API_KEY is not set.")
        return 1
    print(f"Round 16 · FRED date semantics · today={TODAY} · "
          f"key present ({len(KEY)} chars, never printed)\n")
    q = f"api_key={KEY}&file_type=json"

    # ---- Q1: can we stop depending on the default "today"? ---------------
    a = _get("Q1a/default-realtime",
             f"{FRED}/series/observations?series_id=PAYEMS&{q}&limit=1&sort_order=desc",
             "no realtime param — whatever FRED decides 'now' is", cap=420)
    b = _get("Q1b/default-realtime-again",
             f"{FRED}/series/observations?series_id=PAYEMS&{q}&limit=2&sort_order=desc",
             "same shape, different limit — does 'now' move between calls?", cap=420)
    c = _get("Q1c/explicit-today",
             f"{FRED}/series/observations?series_id=PAYEMS&{q}&limit=1"
             f"&sort_order=desc&realtime_start={TODAY}&realtime_end={TODAY}",
             "asking for today's vintage BY NAME — the version we would ship", cap=420)

    # ---- Q2: does a listed release date mean published? ------------------
    fut = _get("Q2a/releases-dates-in-the-future",
               f"{FRED}/releases/dates?{q}&realtime_start={TODAY}"
               f"&realtime_end={FUTURE}&sort_order=asc&limit=6"
               f"&include_release_dates_with_no_data=true",
               "anything returned here has NOT published yet, by definition")
    _get("Q2b/fomc-release-dates",
         f"{FRED}/release/dates?release_id={FOMC_RELEASE}&{q}"
         f"&sort_order=desc&limit=6&include_release_dates_with_no_data=true",
         "the release that looked scheduled rather than published")

    # ---- End to end: a release that really landed this morning -----------
    ser = _get("E2E/series-in-todays-release",
               f"{FRED}/release/series?release_id={EMPIRE_STATE_RELEASE}&{q}&limit=3",
               "Empire State published 08:30 ET today — what series does it carry?",
               cap=900)
    sid = None
    for s in (ser or {}).get("seriess") or []:
        sid = s.get("id")
        break
    if sid:
        _get("E2E/first-print-of-that-series",
             f"{FRED}/series/observations?series_id={sid}&{q}"
             f"&output_type=4&realtime_start=1776-07-04&realtime_end=9999-12-31"
             f"&sort_order=desc&limit=3",
             f"{sid} — initial releases, newest first. Does the newest carry "
             f"realtime_start == {TODAY}?", cap=700)

    # ---- verdicts --------------------------------------------------------
    print("=" * 64)
    ra, rb, rc = [(x or {}).get("realtime_start") for x in (a, b, c)]
    print(f"Q1  default said {ra!r} then {rb!r}; explicit-today returned {rc!r}")
    if rc == TODAY:
        print("    => VERDICT: an explicit realtime window IS honoured. Ship "
              "every call with realtime_start/realtime_end set and the "
              "default's wobble stops mattering.")
    else:
        print("    => VERDICT: explicit window NOT honoured. FRED cannot be "
              "trusted to answer 'as of today' and the PM edition must not "
              "claim a release date.")
    if ra != rb:
        print(f"    (and the default really does move between calls: "
              f"{ra} vs {rb} — never rely on it)")

    n_future = len((fut or {}).get("release_dates") or [])
    print(f"\nQ2  release dates returned for {TODAY}..{FUTURE}: {n_future}")
    if n_future:
        print("    => VERDICT: releases/dates INCLUDES SCHEDULED dates. A "
              "listed date does NOT mean published, so 'released this "
              "morning' must be proven from an observation's own vintage, "
              "never from this endpoint.")
    else:
        print("    => VERDICT: no future dates returned — the endpoint appears "
              "to list published releases only. Re-test near a known "
              "announcement before relying on it (§12.4).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
