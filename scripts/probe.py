"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.
"""

from __future__ import annotations

import json

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Round 12. Kabil wants inflation prints that persist until superseded, the
# last FOMC decision, and the market-implied odds of a cut against a hike.
#
# The odds are the hard part and the one already on the quarantine list: CME's
# FedWatch page is a QuikStrike iframe with no data in it, which is why
# "Fed path" has been an open item since day one. Three routes to try -
# CME's own quote service for 30-day Fed Funds futures (from which the
# probabilities are arithmetic), and the two prediction markets that publish
# Fed contracts over a free read API.
CANDIDATES = [
    # --- inflation: BLS public API v1 takes no key at all
    ("bls/cpi-headline",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/CUSR0000SA0"),
    ("bls/cpi-core",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/CUSR0000SA0L1E"),
    ("bls/ppi-final-demand",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/WPSFD4"),
    ("bls/ppi-alt",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/WPUFD4"),
    # --- the policy rate itself, keyless, from the desk that sets it
    ("nyfed/rates-latest",
     "https://markets.newyorkfed.org/api/rates/all/latest.json"),
    # --- odds: CME's quote service for ZQ (30-day Fed Funds futures)
    ("cme/zq-quotes",
     "https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/305/G"),
    ("cme/zq-settlements",
     "https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/305/FUT"),
    # --- odds: prediction markets, free read APIs
    ("kalshi/fed-series",
     "https://api.elections.kalshi.com/trade-api/v2/markets?limit=5&series_ticker=KXFEDDECISION"),
    ("kalshi/search",
     "https://api.elections.kalshi.com/trade-api/v2/series?category=Economics"),
    ("polymarket/fed",
     "https://gamma-api.polymarket.com/markets?closed=false&limit=5&tag_id=100328"),
    ("polymarket/search",
     "https://gamma-api.polymarket.com/events?closed=false&limit=4&order=volume24hr&ascending=false"),
]


def main() -> int:
    print(f"Probing {len(CANDIDATES)} candidates from an Actions runner\n")
    verdicts = []
    for name, url in CANDIDATES:
        print(f"--- {name}\n    {url}")
        try:
            r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {type(exc).__name__}: "
                  f"{' '.join(str(exc).split())[:100]}\n")
            verdicts.append((name, "unreachable"))
            continue

        ctype = r.headers.get("content-type", "?")
        print(f"  HTTP {r.status_code} · {ctype} · {len(r.content):,} bytes")
        if r.ok and "json" in ctype.lower():
            try:
                data = json.loads(r.text)
            except json.JSONDecodeError:
                print("  declared JSON, did not parse")
            else:
                print(f"  {' '.join(json.dumps(data)[:900].split())}")
        elif r.ok:
            print(f"  head: {' '.join(r.text[:200].split())}")
        else:
            print(f"  body: {' '.join(r.text[:160].split())}")
        verdicts.append((name, f"HTTP {r.status_code}"))
        print()

    print("=" * 60)
    for name, verdict in verdicts:
        print(f"{verdict:<16} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
