"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.
"""

from __future__ import annotations

import json
import os
import sys

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
}

# Round 15. Round 14 proved FRED answers a datacenter IP; the key is now a
# repository secret. This round asks the only question that matters next:
# can FRED carry the claim the 14:00 edition wants to make?
#
# The distinction is narrow and decides the whole feature.
#
#   "the current read on August CPI is X"  - latest observation. The brief
#       already does this correctly through BLS, and flags preliminary values.
#
#   "CPI CAME IN at X this morning"        - the value AS FIRST PUBLISHED,
#       plus the date it was released. This is what the market traded. A later
#       revision printed under "came in" would be the right series carrying a
#       materially wrong claim, which is §3.10's shape.
#
# FRED documents output_type=4 as "initial release only" and a realtime window
# for vintage retrieval. Documented is not measured, so both get tested, and
# the decisive check is whether a first release and a current value for the
# SAME observation can actually be told apart. PAYEMS is the test case because
# payrolls are revised in the two months after publication as a matter of
# routine - August 2026 was published 4 September, so it has had one revision
# cycle already.
#
# SECURITY: this prints payloads into an Actions log. The key must never reach
# it. Every URL goes through _redact before printing, and the key is read from
# the environment rather than written in source.
FRED = "https://api.stlouisfed.org/fred"
KEY = (os.environ.get("FRED_API_KEY") or "").strip()

# PAYEMS Aug 2026 = the 2026-08-01 observation, first published 2026-09-04.
SERIES, OBS, FIRST_PUB = "PAYEMS", "2026-08-01", "2026-09-04"


def _redact(url: str) -> str:
    return url.replace(KEY, "***REDACTED***") if KEY else url


def _get(label: str, url: str, note: str = ""):
    print(f"--- {label}\n    {_redact(url)}")
    if note:
        print(f"    ({note})")
    try:
        r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED {type(exc).__name__}: "
              f"{_redact(' '.join(str(exc).split())[:120])}\n")
        return None
    ctype = r.headers.get("content-type", "?")
    print(f"  HTTP {r.status_code} · {ctype} · {len(r.content):,} bytes")
    data = None
    if "json" in ctype.lower():
        try:
            data = json.loads(r.text)
        except json.JSONDecodeError:
            print("  declared JSON, did not parse")
    if data is not None:
        print(f"  {_redact(' '.join(json.dumps(data)[:1400].split()))}")
    else:
        print(f"  body: {_redact(' '.join(r.text[:200].split()))}")
    print()
    return data


def _value(data, obs_date):
    """The observation for obs_date, or None."""
    for o in (data or {}).get("observations") or []:
        if o.get("date") == obs_date:
            return o
    return None


def main() -> int:
    if not KEY:
        print("::error::FRED_API_KEY is not set. Add it as a repository "
              "secret and pass it into the probe workflow's env.")
        return 1
    print(f"Round 15 · FRED payload shape · key present ({len(KEY)} chars, "
          f"never printed)\n")

    q = f"api_key={KEY}&file_type=json"

    # 1. Baseline: does a real key return observations at all?
    _get("fred/observations-latest",
         f"{FRED}/series/observations?series_id={SERIES}&{q}"
         f"&sort_order=desc&limit=3",
         "newest first — proves the key works and shows the default shape")

    # 2. Vintage markers. Without realtime_start/realtime_end in the payload a
    #    first print cannot be distinguished from a revision at all.
    current = _get("fred/observations-current-vintage",
                   f"{FRED}/series/observations?series_id={SERIES}&{q}"
                   f"&observation_start={OBS}&observation_end={OBS}",
                   f"the {OBS} observation as it stands TODAY")

    # 3. The same observation as first published. output_type=4 is documented
    #    as "initial release only"; realtime bounds widen the vintage search.
    first = _get("fred/observations-initial-release",
                 f"{FRED}/series/observations?series_id={SERIES}&{q}"
                 f"&observation_start={OBS}&observation_end={OBS}"
                 f"&output_type=4&realtime_start=1776-07-04"
                 f"&realtime_end=9999-12-31",
                 "output_type=4 — the value as FIRST PUBLISHED")

    # 4. Release dates. "Came in this morning" is a claim about a RELEASE date,
    #    not an observation date. Conflating them is how a month-old figure
    #    gets announced as news.
    _get("fred/series-release",
         f"{FRED}/series/release?series_id={SERIES}&{q}",
         "which release publishes this series")
    _get("fred/releases-dates-recent",
         f"{FRED}/releases/dates?{q}&sort_order=desc&limit=8"
         f"&include_release_dates_with_no_data=false",
         "what has actually published recently")

    # ---- the decisive comparison ----------------------------------------
    print("=" * 64)
    cur_o, first_o = _value(current, OBS), _value(first, OBS)
    print(f"DECISIVE TEST — {SERIES} observation {OBS}")
    print(f"  as it stands today : {cur_o.get('value') if cur_o else 'NOT FOUND'}")
    print(f"  as first published : {first_o.get('value') if first_o else 'NOT FOUND'}")
    if cur_o:
        print(f"  current vintage window: {cur_o.get('realtime_start')} "
              f"-> {cur_o.get('realtime_end')}")
    if first_o:
        print(f"  first   vintage window: {first_o.get('realtime_start')} "
              f"-> {first_o.get('realtime_end')}")

    if not (cur_o and first_o):
        print("\n  VERDICT: one side is missing — cannot separate first print "
              "from revision. The PM edition must fall back to "
              '"latest value for X is ..." rather than "came in at".')
    elif cur_o.get("value") != first_o.get("value"):
        print(f"\n  VERDICT: THEY DIFFER "
              f"({first_o.get('value')} -> {cur_o.get('value')}). FRED can "
              f'support "came in at", and reporting the current value as the '
              f"print would have been wrong by that margin.")
    else:
        print("\n  VERDICT: identical for this observation. Either it has not "
              "been revised yet, or output_type=4 is not doing what the docs "
              "say. Re-test against an older observation before trusting it — "
              "a single matching pair proves nothing (§12.4).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
