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


CANDIDATES = (
    # label, url, beat. Round 14 probed the four accounts Kabil named and
    # three failed; these are the free primaries closest to what those
    # accounts actually do, plus the crypto wires WatcherGuru stands in for.
    ("ForexLive", "https://www.forexlive.com/feed/", "macro squawk"),
    ("FinancialJuice", "https://www.financialjuice.com/feed", "macro squawk"),
    ("MarketWatch top", "http://feeds.marketwatch.com/marketwatch/topstories/",
     "macro"),
    ("MarketWatch RT",
     "http://feeds.marketwatch.com/marketwatch/realtimeheadlines/", "macro"),
    ("Investing.com", "https://www.investing.com/rss/news.rss", "macro"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex", "macro"),
    ("Reuters via GNews",
     "https://news.google.com/rss/search?q=when:1d+site:reuters.com"
     "&hl=en-US&gl=US&ceid=US:en", "wire"),
    ("CNBC economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml"
     "?partnerId=wrss01&id=20910258", "macro"),
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/", "crypto"),
    ("The Block", "https://www.theblock.co/rss.xml", "crypto"),
    ("Cointelegraph", "https://cointelegraph.com/rss", "crypto"),
    ("Decrypt", "https://decrypt.co/feed", "crypto"),
)

# A squawk is not a news site with a faster horse. The discriminator is
# CADENCE: FinancialJuice posts dozens of headlines an hour, CNBC posts a few
# a day. Round 14 measured freshness and reach but never items-per-hour, which
# is the number that actually decides whether a feed can carry "what happened
# since the 09:20 brief".
FRESH_PASS_HOURS = 3.0


def main() -> int:
    """Round 21 — can anything free carry a squawk?

    Kabil asked whether the brief watches @DeItaone, @zerohedge,
    @financialjuice and @WatcherGuru. It watches one, through its website.
    X itself costs $0.005/read with no free tier and Nitter is under
    cease-and-desist, so round 14 probed the four at their primaries and CNBC
    beat three of them (§12.8).

    He now wants headlines in BOTH editions. The PM edition needs a feed that
    says what happened in the last three hours, which is a harder test than
    the AM's eighteen. This round measures four things per candidate:

      - does the BRIEF'S OWN PARSER read it (not a probe-local one - round 18
        failed on exactly that, and §3.28 was a wrong verdict caused by this
        probe's own headers);
      - how old is the newest item (WatcherGuru died here at 41.9h);
      - how far back does the feed reach;
      - ITEMS PER HOUR across the feed's own span - the squawk test.
    """
    head(1, "Free squawk candidates, read with the brief's own client",
         f"PASS needs: 200, the brief's parser finds items, every item dated, "
         f"newest under {FRESH_PASS_HOURS:.0f}h. Cadence is reported for all.")

    results = []
    for label, url, beat in CANDIDATES:
        print(f"\n  --- {label} ({beat}) ---")
        raw = None
        try:
            r = requests.get(url, timeout=TIMEOUT, headers=sources.HEADERS)
            print(f"    {url}")
            print(f"    HTTP {r.status_code} · {len(r.content):,} bytes · "
                  f"{r.headers.get('content-type', '?')[:40]}")
            if r.status_code != 200:
                print(f"    body: {r.text[:120]}")
                results.append((label, beat, "FAIL", f"HTTP {r.status_code}"))
                continue
            raw = r.content
        except Exception as exc:  # noqa: BLE001
            print(f"    FAILED {type(exc).__name__}: {str(exc)[:110]}")
            results.append((label, beat, "FAIL", type(exc).__name__))
            continue

        # The brief's parser, not one written for this probe.
        try:
            parsed = sources._rss_items(raw)
        except Exception as exc:  # noqa: BLE001
            print(f"    parser rejected it: {type(exc).__name__}: "
                  f"{str(exc)[:90]}")
            results.append((label, beat, "FAIL", "unparseable"))
            continue

        dated = [w for _t, _l, w in parsed if w is not None]
        print(f"    items {len(parsed)} · dated {len(dated)}")
        if not dated:
            # §12.8: a 200 with no usable timestamp cannot support a window.
            print("    NO PARSEABLE TIMESTAMPS - cannot support a window")
            results.append((label, beat, "FAIL", "no timestamps"))
            continue

        dated = sorted(dated, reverse=True)
        newest = (NOW - dated[0]).total_seconds() / 3600
        span = (dated[0] - dated[-1]).total_seconds() / 3600
        per_hour = (len(dated) / span) if span > 0.01 else float("inf")
        print(f"    newest {newest:.1f}h old · reaches back {span:.1f}h")
        print(f"    cadence {per_hour:.1f} items/hour")
        sample = [t for t, _l, w in parsed if w is not None][:2]
        for t in sample:
            print(f"      · {t[:96]}")

        if newest <= FRESH_PASS_HOURS and len(dated) == len(parsed):
            verdict, why = "PASS", f"{newest:.1f}h, {per_hour:.1f}/h"
        elif newest <= FRESH_PASS_HOURS:
            verdict, why = "PARTIAL", f"{len(parsed) - len(dated)} undated"
        else:
            verdict, why = "FAIL", f"newest {newest:.1f}h old"
        print(f"    -> {verdict}: {why}")
        results.append((label, beat, verdict, why))

    print("\n" + "=" * 68)
    print(f"{'SOURCE':<20}{'BEAT':<14}{'VERDICT':<10}WHY")
    print("=" * 68)
    for label, beat, verdict, why in results:
        print(f"{label:<20}{beat:<14}{verdict:<10}{why}")
    print()
    print("A PM edition asks what happened in the last ~3.5 hours. Anything")
    print("whose cadence is under ~1 item/hour can fill the AM brief but will")
    print("be empty most afternoons, and an empty section that is empty by")
    print("construction is worse than no section - it reads as 'nothing")
    print("happened' (§3.16).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
