"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.

The point is to answer, from an actual Actions runner, the only question that
matters about a candidate: does it respond, and what shape is the response?
Farside is the standing lesson — it is a plain public page that works from a
browser and 403s a datacenter IP, and no amount of reading its documentation
would have revealed that. So: probe, read the output, then write a fetcher
against what actually came back.
"""

from __future__ import annotations

import json
import sys

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

CANDIDATES = [
    # --- gap 1: ETF flows. Farside has 403'd every run for 12 days. ---------
    ("etf/farside-control", "https://farside.co.uk/btc/"),
    ("etf/bykaranteli", "https://bykaranteli.com/etf"),
    ("etf/tftc", "https://www.tftc.io/bitcoin-etf-flows"),

    # --- gap 2: derivatives. CoinGlass has no free tier; Binance's futures
    # market-data endpoints are public and keyless. ------------------------
    ("deriv/binance-funding",
     "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT"),
    ("deriv/binance-oi",
     "https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT"),
    ("deriv/binance-oi-hist",
     "https://fapi.binance.com/futures/data/openInterestHist"
     "?symbol=BTCUSDT&period=1d&limit=2"),

    # --- gap 3: AAII sentiment. Never tested from a runner. ----------------
    ("aaii/survey", "https://www.aaii.com/sentimentsurvey"),

    # --- control: a feed we know works, to prove the probe itself is sane --
    ("control/forexfactory-thisweek",
     "https://nfs.faireconomy.media/ff_calendar_thisweek.json"),
    # And the URL the brief has been calling a "broken feed" - research says
    # ForexFactory never published a next-week variant at all.
    ("control/forexfactory-nextweek",
     "https://nfs.faireconomy.media/ff_calendar_nextweek.json"),
]


def describe(body: str, ctype: str) -> str:
    """A few lines that say what shape the payload is."""
    if "json" in ctype.lower():
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return "  declared JSON but did not parse"
        if isinstance(data, list):
            head = data[0] if data else None
            return (f"  JSON array, {len(data)} items\n"
                    f"  first item keys: "
                    f"{sorted(head) if isinstance(head, dict) else type(head).__name__}")
        if isinstance(data, dict):
            return f"  JSON object, keys: {sorted(data)[:20]}"
        return f"  JSON {type(data).__name__}"

    lower = body.lower()
    hints = []
    if "<table" in lower:
        hints.append(f"{lower.count('<table')} <table>")
    for marker in ("application/json", "__next_data__", "window.__", ".csv"):
        if marker in lower:
            hints.append(f"contains {marker!r}")
    return f"  HTML/text{'; ' + ', '.join(hints) if hints else ''}"


def main() -> int:
    print(f"Probing {len(CANDIDATES)} candidates from an Actions runner\n")
    verdicts = []
    for name, url in CANDIDATES:
        print(f"--- {name}\n    {url}")
        try:
            r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {type(exc).__name__}: "
                  f"{' '.join(str(exc).split())[:120]}\n")
            verdicts.append((name, "unreachable"))
            continue

        ctype = r.headers.get("content-type", "?")
        print(f"  HTTP {r.status_code} · {ctype} · {len(r.content):,} bytes")
        if r.ok:
            print(describe(r.text, ctype))
            print(f"  head: {' '.join(r.text[:220].split())}")
            verdicts.append((name, f"OK {r.status_code}"))
        else:
            verdicts.append((name, f"HTTP {r.status_code}"))
        print()

    print("=" * 60)
    for name, verdict in verdicts:
        print(f"{verdict:<16} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
