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


GNEWS = ("https://news.google.com/rss/search?q={q}"
         "&hl=en-US&gl=US&ceid=US:en")

# Round 21 made Reuters-via-Google-News the only squawk-grade feed at
# 4.3 items/hour. Round 21's query was site:reuters.com with no scope, and
# the first live PM edition printed:
#
#   Pirates' Brandon Lowe takes HR barrage into finale vs. Royals - Reuters
#   Olympic dreams flicker as teqball awards first Asian Games medals
#
# A title deny-list does not fix that. "Pirates", "Royals", "HR barrage" and
# "finale" contain no sports word a filter would catch, and §3.6 is the
# section about what happens when a word list is asked to do semantic work.
# Reuters' own URLs are already a taxonomy - reuters.com/markets,
# /business, /world - so the scope belongs in the QUERY, not in a guess about
# the title.
#
# Narrowing costs cadence. This round measures how much, because a scoped
# feed that drops to 0.3/h is no longer worth having over the five already
# wired.
SCOPES = (
    ("unscoped (round 21)", "when:1d+site:reuters.com"),
    ("markets", "when:1d+site:reuters.com/markets"),
    ("business", "when:1d+site:reuters.com/business"),
    ("markets+business", "when:1d+(site:reuters.com/markets+OR+"
                         "site:reuters.com/business)"),
    ("markets+business+world",
     "when:1d+(site:reuters.com/markets+OR+site:reuters.com/business+OR+"
     "site:reuters.com/world)"),
)

FRESH_PASS_HOURS = 3.0


def main() -> int:
    """Round 22 — scope Reuters with its own taxonomy, and count the cost.

    PASS still needs a fresh, fully dated feed. The number that decides which
    scope ships is cadence: it has to stay high enough to fill a 3.5-hour PM
    window, and the titles have to stop being about baseball.
    """
    head(1, "Reuters via Google News, scoped by Reuters' own URL sections",
         "Same client and same parser as the brief. Cadence is the cost of "
         "narrowing; the sample titles are whether it worked.")

    rows = []
    for label, q in SCOPES:
        print(f"\n  --- {label} ---")
        url = GNEWS.format(q=q)
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=sources.HEADERS)
            print(f"    HTTP {r.status_code} · {len(r.content):,} bytes")
            if r.status_code != 200:
                rows.append((label, "FAIL", f"HTTP {r.status_code}", 0.0))
                continue
            parsed = sources._rss_items(r.content)
        except Exception as exc:  # noqa: BLE001
            print(f"    FAILED {type(exc).__name__}: {str(exc)[:110]}")
            rows.append((label, "FAIL", type(exc).__name__, 0.0))
            continue

        dated = sorted([w for _t, _l, w in parsed if w is not None], reverse=True)
        if not dated:
            print("    no parseable timestamps")
            rows.append((label, "FAIL", "no timestamps", 0.0))
            continue
        newest = (NOW - dated[0]).total_seconds() / 3600
        span = (dated[0] - dated[-1]).total_seconds() / 3600
        per_hour = (len(dated) / span) if span > 0.01 else float("inf")
        print(f"    items {len(parsed)} · newest {newest:.1f}h · "
              f"span {span:.1f}h · cadence {per_hour:.1f}/h")
        for t, _l, _w in parsed[:6]:
            print(f"      · {t[:94]}")
        verdict = "PASS" if newest <= FRESH_PASS_HOURS else "FAIL"
        rows.append((label, verdict, f"{newest:.1f}h", per_hour))

    print("\n" + "=" * 68)
    print(f"{'SCOPE':<26}{'VERDICT':<9}{'NEWEST':<9}CADENCE")
    print("=" * 68)
    for label, verdict, why, per_hour in rows:
        print(f"{label:<26}{verdict:<9}{why:<9}{per_hour:.1f}/h")
    print()
    print("Read the SAMPLE TITLES, not just the cadence. The unscoped feed")
    print("passed round 21 on numbers alone and was full of baseball.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
