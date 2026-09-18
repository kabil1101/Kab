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
    print(f"Round 19 · {NOW:%Y-%m-%d %H:%M} UTC · using sources.HEADERS\n")

    # ---- 1-3. can OKX support a 24h aggregate? --------------------------
    for n, params, note in (
        # `state` is REQUIRED and round 19's first attempt dropped it, so
        # targets 1-3 tested nothing and returned `50014 Parameter state can
        # not be empty`. Third probe bug of mine in three rounds, after the
        # Senate parser and the Yahoo headers. Logged rather than quietly
        # fixed - a probe that fails because of its own client looks exactly
        # like a source that does not work.
        (1, {"instType": "SWAP", "uly": "BTC-USD", "state": "filled",
             "limit": "100"},
         "coin-margined BTC, the biggest page OKX allows"),
        (2, {"instType": "SWAP", "uly": "BTC-USDT", "state": "filled",
             "limit": "100"},
         "USDT-margined BTC - a different book, usually the deeper one"),
        (3, {"instType": "SWAP", "instFamily": "ETH-USDT", "state": "filled",
             "limit": "100"},
         "ETH, to see whether one call per underlying is the shape"),
    ):
        head(n, f"OKX liquidations · {note.split(' - ')[0]}",
             "Round 18 proved the endpoint answers. This asks whether one "
             "call can carry a 24h total, or whether the line has to be "
             "'recent' instead.")
        d = _get(OKX, params, note=note)
        rows = _rows(d)
        print(f"    flattened rows: {len(rows)}")
        sp = _span(rows)
        if sp:
            newest, oldest, hours = sp
            print(f"    newest {newest:%Y-%m-%d %H:%M}Z · oldest "
                  f"{oldest:%Y-%m-%d %H:%M}Z · span {hours:.2f}h")
            # The claim worth printing needs a notional, so check the pieces
            # are actually there rather than assuming the shape from one row.
            longs = [r for r in rows if r.get("posSide") == "long"]
            shorts = [r for r in rows if r.get("posSide") == "short"]
            missing = [k for k in ("sz", "bkPx", "ts", "posSide")
                       if any(k not in r for r in rows)]
            print(f"    longs {len(longs)} · shorts {len(shorts)} · "
                  f"missing keys: {missing or 'none'}")
            try:
                notional = sum(float(r["sz"]) * float(r["bkPx"]) for r in rows)
                print(f"    notional across the page: ${notional:,.0f} "
                      f"(units unverified - sz may be contracts, not coins)")
            except Exception as exc:  # noqa: BLE001
                print(f"    could not total: {exc}")
        if rows[:1]:
            print(f"    sample row: {json.dumps(rows[0], sort_keys=True)}")

    # ---- 4. was the Yahoo verdict mine? ---------------------------------
    head(4, "Yahoo, with the brief's own headers",
         "§3.28 claims Yahoo rate-limits a runner. Two probe rounds drew 429 "
         "with a BROWSER user agent; the brief's seven symbols succeeded "
         "minutes either side with a plain one. If these answer, the finding "
         "was my client.")
    for sym, why in (("IBIT", "the ETF's secondary market"),
                     ("BZ=F", "Brent, for the Brent-WTI spread"),
                     ("BTC=F", "CME BTC futures - the addendum's target 10")):
        d = _get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}",
                 {"range": "5d", "interval": "1d"}, note=why)
        try:
            res = d["chart"]["result"][0]
            meta = res["meta"]
            stamps = res.get("timestamp") or []
            closes = (res["indicators"]["quote"][0].get("close") or [])
            vols = (res["indicators"]["quote"][0].get("volume") or [])
            last = (datetime.fromtimestamp(stamps[-1], timezone.utc)
                    if stamps else None)
            print(f"    {meta.get('symbol')} {meta.get('regularMarketPrice')} "
                  f"{meta.get('currency')} · {meta.get('fullExchangeName')}")
            print(f"    bars {len(stamps)} · last bar "
                  f"{last:%Y-%m-%d %H:%M}Z · close {closes[-1] if closes else None}"
                  f" · volume {vols[-1] if vols else None}")
        except Exception:  # noqa: BLE001
            pass

    print("\n" + "=" * 64)
    print("If target 4 answered, §3.28 was this probe's headers rather than")
    print("Yahoo's policy, and IBIT / Brent / CME BTC have never been tested.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
