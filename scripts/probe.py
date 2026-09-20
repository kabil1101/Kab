"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.

Round 19 — can OKX carry the claim, and was the Yahoo verdict mine?
===================================================================

Round 18 established that OKX answers keyless with `sz`, `ts` and `posSide`.
That is enough to know liquidations are reachable and **not** enough to write
a fetcher: one call returned five rows of one underlying, and the line worth
printing is *"$X of longs liquidated in the last 24h"*.

So: how far back does one call reach, how many rows come with it, does the
USDT-margined book answer the same way, and can a 24-hour total be assembled
without paging through the night?

And a correction to check. §3.28 says Yahoo rate-limits an Actions runner, on
two rounds of `429` across two hosts. But the brief's own Yahoo calls
succeeded in four runs minutes either side of both probes — seven symbols, no
failures. The difference is not the host: **the probe sent a browser-shaped
User-Agent with a JSON `Accept`, and `sources.py` sends a plain one.** This
round repeats the call with the brief's own headers. If they answer, §3.28 was
my client and not Yahoo's policy, and IBIT, Brent and CME BTC are all still
untested rather than blocked.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

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


def main() -> int:
    """Round 20 — what unit does FRED actually return?

    The brief printed, on 20 September 2026:

        **Treasury account** $877,028bn
        **Bank reserves** $3,013,794bn

    Bank reserves are about $3.0 trillion. Printed as billions, that line
    claims three quadrillion dollars. `PLUMBING_SERIES` declares all three
    series as "$bn" and `_plumbing_lines` hardcodes "bn" on the value without
    reading even that field - so the label is an assumption twice over.

    §3.9 for the sixth time: present, sourced, correctly stamped, materially
    misleading. The assumption was never checked against FRED's own metadata,
    and this round checks it rather than guessing a second time. The key stays
    out of the log: _get prints the URL, never the params.
    """
    key = (os.environ.get("FRED_API_KEY") or "").strip()
    if not key:
        print("FRED_API_KEY is not set; nothing to probe.")
        return 1

    head(1, "FRED series metadata — the declared unit of every series we read",
         "Nine series across BACKDROP and the plumbing. `units` is what FRED "
         "says the numbers are in; the brief currently asserts its own.")
    rows = []
    for sid, label, assumed in (
            ("UNRATE", "Unemployment", "%"),
            ("T10Y2Y", "10Y-2Y spread", "pp"),
            ("CPIAUCSL", "CPI", "index"),
            ("RRPONTSYD", "Reverse repo", "$bn"),
            ("WTREGEN", "Treasury account", "$bn"),
            ("WRESBAL", "Bank reserves", "$bn")):
        meta = _get("https://api.stlouisfed.org/fred/series",
                    {"series_id": sid, "api_key": key, "file_type": "json"},
                    note=f"{label} — brief assumes {assumed}")
        units = units_short = title = "?"
        if meta:
            try:
                srs = meta["seriess"][0]
                units = srs.get("units")
                units_short = srs.get("units_short")
                title = srs.get("title")
            except Exception:  # noqa: BLE001
                print(f"    unexpected shape: {json.dumps(meta)[:200]}")
        obs = _get("https://api.stlouisfed.org/fred/series/observations",
                   {"series_id": sid, "api_key": key, "file_type": "json",
                    "sort_order": "desc", "limit": 1})
        latest = "?"
        if obs:
            try:
                latest = obs["observations"][0]["value"]
            except Exception:  # noqa: BLE001
                pass
        print(f"    {sid:<10} assumed={assumed:<6} FRED units={units!r} "
              f"({units_short!r})")
        print(f"    {'':<10} latest={latest} · {title}")
        rows.append((sid, assumed, units_short, latest))

    print("\n" + "=" * 64)
    print("VERDICT TABLE — what the brief must print for each series")
    print("=" * 64)
    for sid, assumed, units_short, latest in rows:
        print(f"  {sid:<10} brief says {assumed:<6} FRED says {units_short}")
    print()
    print("A series FRED reports in Millions must be divided by 1,000 before")
    print("the brief calls it billions - or printed with FRED's own unit. The")
    print("scale is a property of the series, so it belongs beside the id.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
