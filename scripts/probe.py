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
# Round 13. Round 12 answered the hard question: the Fed-path odds this
# project has recorded as having no free source since day one are available
# from two independent prediction markets, both keyless. CME itself is 403 to
# datacenter IPs - the Farside lesson again - so FedWatch stays quarantined
# and the odds come from elsewhere.
#
# This round reads the shapes: which Kalshi contracts exist for the NEXT
# meeting and how their strikes are labelled, what Polymarket's September
# event carries, and what BLS actually returns per series (v1 has no
# calculations, so month-over-month and year-over-year have to be computed
# from the index values, which means knowing exactly what the index looks
# like).
CANDIDATES = [
    ("kalshi/events-open",
     "https://api.elections.kalshi.com/trade-api/v2/events"
     "?series_ticker=KXFEDDECISION&status=open&limit=3"),
    ("kalshi/markets-open",
     "https://api.elections.kalshi.com/trade-api/v2/markets"
     "?series_ticker=KXFEDDECISION&status=open&limit=20"),
    ("polymarket/sept-event",
     "https://gamma-api.polymarket.com/events?slug=fed-decision-in-september-762"),
    ("bls/cpi-headline",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/CUSR0000SA0"),
    ("bls/ppi-final-demand",
     "https://api.bls.gov/publicAPI/v1/timeseries/data/WPSFD4"),
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
                blob = json.dumps(data)
                print(f"  {' '.join(blob[:2600].split())}")
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
