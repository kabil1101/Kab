"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.

Round 18 — the liquidation question, and five things round 17 left open
======================================================================

**The headline target is liquidations, and it is the largest single gap
between Kabil's stated framework and this system.** His framework opens with
*"liquidation cascades, not support/resistance magic"*, and the brief carries
no liquidation data at all: not the level, not the 24h total, not the
clusters.

The register's verdict is `S2` — CoinGlass, no free tier, $29/mo — and
PROJECT_STATE §12.2 already marks that *"unconfirmed rather than settled"*.
§12.4a is precise about the shape: **CoinGlass being paid is a property of
that route, not a property of the world.** Three large venues run public REST
APIs and not one has ever been called from here.

Also in this round, because a probe round costs one dispatch whether it
carries one target or eight (§12.6):

  - **Kalshi's midterm tickers.** The plan calls Kalshi probe-free because it
    is already LIVE. That is true of `KXFEDDECISION`; the House and Senate
    control contracts are different tickers nobody has looked at.
  - **State's real feed URLs**, read off its own index page instead of
    guessed a fourth time.
  - **The Senate schema**, which round 17's parser could not read because it
    looks for RSS `item`/Atom `entry` and the Senate uses neither. That was a
    probe bug, not a dead source.
  - **Yahoo IBIT and Brent**, which both returned `429` and therefore tested
    nothing about either instrument.
  - **CME BTC futures** — addendum target 10. The addendum is OPEN and says
    build nothing from it; a probe is not a build, and §12.3 wants the fact
    on the record before anyone considers it.
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/json,application/xml,*/*;q=0.8",
    "Cache-Control": "no-cache",
}
NOW = datetime.now(timezone.utc)
SECRETS = [v for v in (os.environ.get("FRED_API_KEY"),) if (v or "").strip()]


def _redact(text: str) -> str:
    for s in SECRETS:
        text = text.replace(s, "***REDACTED***")
    return text


def _http(url, note="", params=None):
    print(f"    {_redact(url)}")
    if note:
        print(f"    ({note})")
    try:
        r = requests.get(url, headers=BROWSER, params=params, timeout=TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED {type(exc).__name__}: "
              f"{_redact(' '.join(str(exc).split())[:140])}")
        return None
    ctype = (r.headers.get("content-type") or "?").split(";")[0]
    print(f"    HTTP {r.status_code} · {len(r.content):,} bytes · {ctype}")
    return r


def _show(r, cap=520):
    if r is None:
        return None
    try:
        data = r.json()
    except Exception:  # noqa: BLE001
        print(f"    body: {_redact(' '.join(r.text[:240].split()))}")
        return None
    print(f"    {_redact(' '.join(json.dumps(data)[:cap].split()))}")
    return data


def head(n, title, why):
    print(f"\n=== {n}. {title}\n    WHY: {why}")


def main() -> int:
    print(f"Round 18 · liquidations, and round 17's leftovers · "
          f"{NOW:%Y-%m-%d %H:%M} UTC\n")

    # ---- 1. liquidations, three venues, none ever probed -----------------
    # Pass test is deliberately strict: a 200 is not enough. The payload has
    # to carry a SIZE and a TIMESTAMP, or it cannot support "$180m of longs
    # liquidated in the last 24h" - which is the claim worth printing.
    head(1, "OKX — public liquidation orders",
         "The most specific documented endpoint of the three. Pass = 200 with "
         "sized, timestamped rows.")
    okx = _show(_http("https://www.okx.com/api/v5/public/liquidation-orders",
                      params={"instType": "SWAP", "state": "filled",
                              "uly": "BTC-USD", "limit": "5"}))
    if okx and isinstance(okx.get("data"), list) and okx["data"]:
        print(f"    rows: {len(okx['data'])} · keys: "
              f"{sorted(okx['data'][0])[:10]}")

    head(2, "Bybit — recent liquidations",
         "Second venue. Bybit's v5 REST may only expose liquidations over "
         "websocket; a 4xx here is a real answer, not a failure.")
    _show(_http("https://api.bybit.com/v5/market/recent-trade",
                params={"category": "linear", "symbol": "BTCUSDT",
                        "limit": "1"},
                note="trade endpoint first, to prove the host answers at all"))
    _show(_http("https://api.bybit.com/v5/market/liq-records",
                params={"category": "linear", "symbol": "BTCUSDT"},
                note="plausible path, pattern-matched and unverified"))

    head(3, "Bitget — liquidation / long-short data",
         "Third venue. Same test.")
    _show(_http("https://api.bitget.com/api/v2/mix/market/ticker",
                params={"symbol": "BTCUSDT", "productType": "usdt-futures"},
                note="ticker first, to prove the host answers"))
    _show(_http("https://api.bitget.com/api/v2/mix/market/liquidation-orders",
                params={"symbol": "BTCUSDT", "productType": "usdt-futures"},
                note="plausible path, pattern-matched and unverified"))

    head(4, "Coinalyze — the free tier behind a key",
         "D2 allows a free tier behind a free signup. The register marks "
         "coinalyze PAGES as S6 (client-rendered); the API is a different "
         "thing and has never been tried. A 401 means auth is the only "
         "barrier - round 14's test for FRED, which is how that key got "
         "requested.")
    _show(_http("https://api.coinalyze.net/v1/liquidation-history",
                params={"symbols": "BTCUSD_PERP.A", "interval": "1hour",
                        "from": "0", "to": "9999999999"},
                note="deliberately NO key - what does it say about auth?"))

    # ---- 5. Kalshi midterms ---------------------------------------------
    head(5, "Kalshi — midterm control tickers",
         "EXPECTATIONS already reads KXFEDDECISION off this API, keyless. "
         "House and Senate control are DIFFERENT contracts and nobody has "
         "looked at them. Pass = a series ticker that resolves to live "
         "markets with prices.")
    for series in ("KXHOUSE", "KXSENATE", "KXMIDTERMS", "KXHOUSECONTROL"):
        d = _show(_http("https://api.elections.kalshi.com/trade-api/v2/markets",
                        params={"series_ticker": series, "status": "open",
                                "limit": "3"},
                        note=f"series_ticker={series}"), cap=300)
        if d and d.get("markets"):
            for m in d["markets"][:3]:
                print(f"      · {m.get('ticker')} — {m.get('title')} "
                      f"· yes_bid {m.get('yes_bid')} yes_ask {m.get('yes_ask')}")

    # ---- 6. State Department, read rather than guessed -------------------
    head(6, "State Department — feed URLs off its own index",
         "Round 17 guessed three URLs: one 404, one 200 serving a PNG, one "
         "HTML index. Stop guessing and read the index.")
    idx = _http("https://www.state.gov/rss-feeds/")
    if idx is not None and idx.status_code == 200:
        hrefs = sorted(set(re.findall(
            r'href="([^"]*(?:feed|rss)[^"]*)"', idx.text, re.I)))
        print(f"    feed-ish links found: {len(hrefs)}")
        for h in hrefs[:12]:
            print(f"      · {h}")

    # ---- 7. the Senate schema, which my own parser could not read --------
    head(7, "Senate hearings — what the XML actually contains",
         "Round 17 reported 'no items parsed'. The feed answered 200 with "
         "23KB of XML; the parser looks for RSS item / Atom entry and the "
         "Senate uses its own schema. My bug, not a dead source.")
    r = _http("https://www.senate.gov/general/committee_schedules/hearings.xml")
    if r is not None and r.status_code == 200:
        try:
            root = ET.fromstring(r.content.lstrip(b"\xef\xbb\xbf"))
            tags = Counter(el.tag.rsplit("}", 1)[-1] for el in root.iter())
            print(f"    root: <{root.tag}> · element names: "
                  f"{tags.most_common(10)}")
            first = next((el for el in root
                          if len(list(el))), None)
            if first is not None:
                print(f"    first record <{first.tag}>:")
                for child in list(first)[:8]:
                    txt = " ".join((child.text or "").split())[:70]
                    print(f"      · {child.tag.rsplit('}', 1)[-1]}: {txt}")
        except ET.ParseError as exc:
            print(f"    XML did not parse: {exc}")

    # ---- 8. Yahoo, which answered nothing last round ---------------------
    head(8, "Yahoo IBIT / Brent / CME BTC — a second attempt",
         "Round 17 drew 429 on both, so NEITHER instrument was tested. "
         "query2 host this time. CME BTC is the addendum's target 10 - "
         "probing it is not building it.")
    for sym, note in (("IBIT", "secondary market for the ETF"),
                      ("BZ=F", "Brent, for the Brent-WTI spread"),
                      ("BTC=F", "CME BTC futures — addendum target 10")):
        d = _show(_http(f"https://query2.finance.yahoo.com/v8/finance/chart/{sym}",
                        params={"range": "5d", "interval": "1d"},
                        note=note), cap=160)
        try:
            meta = d["chart"]["result"][0]["meta"]
            print(f"      price {meta.get('regularMarketPrice')} · "
                  f"{meta.get('currency')} · {meta.get('fullExchangeName')}")
        except Exception:  # noqa: BLE001
            pass

    print("\n" + "=" * 64)
    print("A 200 is not a pass. The liquidation targets need a SIZE and a")
    print("TIMESTAMP in the payload, or they cannot support the only claim")
    print("worth printing. Write every result into §12.2, dead ones included.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
