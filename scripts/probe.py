"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.

Round 17 — nine targets, one dispatch
=====================================

Batched on purpose. §12.6: every round costs a commit, a dispatch and a log
read, so nine separate rounds would cost nine of each. The targets do not
depend on one another, so there is no reason to serialise them.

**Every feed target answers three questions, not one.** Round 14's lesson was
WatcherGuru: HTTP 200, perfectly formed items, every one timestamped — and the
newest was 41.9 hours old. A feed that answers is not a feed that carries
signal. So each one reports:

    status · item count · newest-item age · how far back the window reaches
    · three real titles

The titles are what turn "it works" into "it is useful". A feed carrying forty
routine notices a day and one market-moving line is technically live and
practically noise, and only the samples show which one it is.

Guessed, and flagged as such: every URL for targets 1, 2, 8 and 9 is
pattern-matched rather than verified. Government sites restructure. That is why
each target carries a list of candidates rather than one address, and why a
404 on the first is data rather than a failure.

Known risk carried in: government hosts are a plausible `S1`. Farside, Binance
and CME all answer a browser and block a datacenter IP. If whitehouse.gov does
the same, this probe is how that is found out — not the wiring.
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "application/rss+xml,application/xml,application/json,*/*;q=0.8",
    # Round 15 saw two calls seconds apart disagree about what "today" was.
    # If an edge cache is in play, say so at the door rather than guessing.
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

NOW = datetime.now(timezone.utc)
# Carried from round 15: an Actions log is readable, and a key that reaches one
# is a key that has to be rotated. Nothing in round 17 needs a key, but the
# redaction stays in the plumbing so the next round cannot forget it.
SECRETS = [v for v in (os.environ.get("FRED_API_KEY"),) if (v or "").strip()]


def _redact(text: str) -> str:
    for s in SECRETS:
        text = text.replace(s, "***REDACTED***")
    return text


def _age(dt: datetime | None) -> str:
    if dt is None:
        return "undated"
    hours = (NOW - dt).total_seconds() / 3600.0
    if abs(hours) < 48:
        return f"{hours:.1f}h"
    return f"{hours / 24:.1f}d"


def _when(text) -> datetime | None:
    """A datetime out of whatever a feed happens to use, or None."""
    text = (text or "").strip()
    if not text:
        return None
    try:                                   # RFC 822 — most RSS
        dt = parsedate_to_datetime(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:                      # noqa: BLE001
        pass
    try:                                   # ISO 8601 — Atom, JSON APIs
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _strip(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _items(xml_text: str):
    """(title, published) for every entry, RSS or Atom, namespaces or not."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(f"  XML did not parse: {exc}")
        return []
    out = []
    for node in root.iter():
        if _strip(node.tag) not in ("item", "entry"):
            continue
        title, when = None, None
        for child in node:
            name = _strip(child.tag)
            if name == "title" and title is None:
                title = " ".join((child.text or "").split())
            elif name in ("pubdate", "published", "updated", "date") and when is None:
                when = _when(child.text)
        out.append((title or "(no title)", when))
    return out


def _http(url: str, note: str = ""):
    print(f"    {_redact(url)}")
    if note:
        print(f"    ({note})")
    try:
        r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
    except Exception as exc:               # noqa: BLE001
        print(f"    FAILED {type(exc).__name__}: "
              f"{_redact(' '.join(str(exc).split())[:120])}")
        return None
    ctype = (r.headers.get("content-type") or "?").split(";")[0]
    print(f"    HTTP {r.status_code} · {len(r.content):,} bytes · {ctype}")
    return r


def feed(n: int, label: str, candidates: list[str], why: str) -> dict:
    """One feed target, reported the same way every time."""
    print(f"\n=== {n}. {label}\n    WHY: {why}")
    best = None
    for url in candidates:
        r = _http(url)
        if r is None or r.status_code != 200:
            continue
        items = _items(r.text)
        if not items:
            print("    200, but no items parsed — not a feed we can read")
            continue
        dated = sorted([w for _, w in items if w], reverse=True)
        newest = dated[0] if dated else None
        oldest = dated[-1] if dated else None
        span = f"{(newest - oldest).days}d" if newest and oldest else "-"
        print(f"    items {len(items)} · dated {len(dated)}/{len(items)} · "
              f"newest {_age(newest)} · window {span}")
        for title, when in items[:3]:
            print(f"      · [{_age(when)}] {title[:96]}")
        best = {"url": url, "items": len(items), "dated": len(dated),
                "newest": newest, "span": span,
                "titles": [t for t, _ in items[:3]]}
        break
    if best is None:
        print("    => no candidate answered with a readable feed")
    return best or {}


def api(n: int, label: str, url: str, why: str, cap: int = 700):
    print(f"\n=== {n}. {label}\n    WHY: {why}")
    r = _http(url)
    if r is None:
        return None
    body = r.text
    data = None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"    not JSON: {_redact(' '.join(body[:200].split()))}")
        return None
    print(f"    {_redact(' '.join(json.dumps(data)[:cap].split()))}")
    return data


def main() -> int:
    print(f"Round 17 · nine targets, one dispatch · {NOW:%Y-%m-%d %H:%M} UTC\n")
    verdicts = []

    # ---- 1-2. the policy primaries -------------------------------------
    # D23 scoped policy to ACTIONS, scheduled announcements and dated plans —
    # not remarks. So the pass test is not "does it publish", it is "does it
    # publish things that were DONE".
    wh = feed(1, "White House",
              ["https://www.whitehouse.gov/presidential-actions/feed/",
               "https://www.whitehouse.gov/news/feed/",
               "https://www.whitehouse.gov/briefing-room/feed/",
               "https://www.whitehouse.gov/feed/"],
              "POLICY DESK tracks Trump through signed actions. Today it reads "
              "the Federal Register, which lags. Pass = >=10 items, newest "
              "<24h, window >=48h.")
    state = feed(2, "State Department",
                 ["https://www.state.gov/rss-feeds/press-releases/feed/",
                  "https://www.state.gov/rss-feeds/secretary-of-state/feed/",
                  "https://www.state.gov/rss-feeds/"],
                 "Rubio is tracked by nothing today. Pass = as above, PLUS at "
                 "least 3 of the last 20 items describing something done "
                 "(sanctions, designations, agreements) rather than said.")

    # ---- 3. Kraken daily candles ---------------------------------------
    # The PM thresholds are fixed percentages, which is regime-blind: +-1.0% on
    # BTC is a shrug at 60 vol and an event at 25. Range-scaling needs trailing
    # daily candles. Kraken is already LIVE for spot, so this is a second
    # endpoint on a proven host rather than a new one.
    k = api(3, "Kraken OHLC (daily)",
            "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440",
            "Unblocks threshold v2. Pass = >=20 daily candles and a 14-day "
            "average daily range in a sane band against spot.", cap=260)
    adr = None
    if k and not k.get("error"):
        rows = next((v for kk, v in (k.get("result") or {}).items()
                     if kk != "last" and isinstance(v, list)), [])
        print(f"    candles: {len(rows)}")
        try:
            last14 = rows[-14:]
            spans = [(float(c[2]) - float(c[3])) / float(c[4]) for c in last14]
            adr = 100 * sum(spans) / len(spans)
            close = float(rows[-1][4])
            print(f"    14-day average daily range: {adr:.2f}% "
                  f"· last close {close:,.0f}")
        except Exception as exc:            # noqa: BLE001
            print(f"    could not compute ADR: {type(exc).__name__}: {exc}")

    # ---- 4. Polymarket, generalisably -----------------------------------
    # The question is NOT "can it return a market". It is "can one call find
    # the NEXT one without the month hardcoded" — a query carrying a date is a
    # query that silently goes stale, which is §3.10's shape.
    api(4, "Polymarket — next FOMC without a hardcoded date",
        "https://gamma-api.polymarket.com/markets?closed=false&limit=5"
        "&order=volumeNum&ascending=false&tag=fed",
        "Decides whether EXPECTATIONS can carry geopolitical odds. Pass = a "
        "keyless call returning the NEXT meeting with a mid price and no date "
        "in the query.", cap=900)

    # ---- 5. CoinGecko stablecoins ---------------------------------------
    # D24: supply AND dominance, never dominance alone. A dominance spike in a
    # selloff is mostly arithmetic — the denominator fell.
    g = api(5, "CoinGecko /global — stablecoin keys",
            "https://api.coingecko.com/api/v3/global",
            "Does the call the brief ALREADY makes carry usdt and usdc, or is "
            "a second endpoint needed? Pass = both present.", cap=120)
    if g:
        pct = ((g.get("data") or {}).get("market_cap_percentage") or {})
        have = {k2: round(v, 3) for k2, v in pct.items()
                if k2 in ("usdt", "usdc", "dai", "btc", "eth")}
        print(f"    keys present: {have}")
        verdicts.append(("5 CoinGecko stablecoins",
                         "PASS — usdt and usdc both in the existing call"
                         if {"usdt", "usdc"} <= set(pct)
                         else f"PARTIAL — found {sorted(set(pct) & {'usdt','usdc'})}"))

    # ---- 6-7. Yahoo, which is already carrying thirteen lines -----------
    # Logged in §12.2 as host concentration: one outage takes most of MACRO
    # plus part of FLOWS. These two make it fifteen. Recorded, not fixed.
    for n, sym, why in (
        (6, "IBIT", "FLOWS covers the primary market; IBIT is the secondary. "
                    "At 09:20 LIS (04:20 ET) the last print is YESTERDAY'S "
                    "close and must be labelled so. Pass = volume and a usable "
                    "timestamp outside cash hours."),
        (7, "BZ=F", "Brent, and Brent-WTI as the cheap read on seaborne risk "
                    "premium. Pass = same call shape as CL=F, which is live."),
    ):
        d = api(n, f"Yahoo {sym}",
                f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}"
                f"?range=5d&interval=1d",
                why, cap=200)
        try:
            res = d["chart"]["result"][0]
            meta = res["meta"]
            stamps = res.get("timestamp") or []
            vols = (res["indicators"]["quote"][0].get("volume") or [])
            last = datetime.fromtimestamp(stamps[-1], timezone.utc) if stamps else None
            print(f"    price {meta.get('regularMarketPrice')} "
                  f"· currency {meta.get('currency')} "
                  f"· exchange {meta.get('fullExchangeName')}")
            print(f"    last bar {last:%Y-%m-%d %H:%M}Z ({_age(last)}) "
                  f"· volume {vols[-1] if vols else None}")
        except Exception as exc:            # noqa: BLE001
            print(f"    shape not as expected: {type(exc).__name__}: {exc}")

    # ---- 8. CourtListener ------------------------------------------------
    # The OpenAI entry (1 Oct) has no confirmation route without this. A
    # watchlist date with no way to confirm it decays into CONFIRM wallpaper.
    api(8, "CourtListener — federal dockets, keyless",
        "https://www.courtlistener.com/api/rest/v4/search/"
        "?q=OpenAI&type=r&order_by=dateFiled%20desc",
        "The only free primary that can carry court dates. Pass = 200 and a "
        "docket retrievable by case.", cap=600)

    # ---- 9. Congressional calendars -------------------------------------
    # Catches Warsh testimony and Bessent appearances BEFORE they happen,
    # which is the whole point of a forward calendar.
    feed(9, "Senate committee hearings",
         ["https://www.senate.gov/general/committee_schedules/hearings.xml"],
         "Forward-dated hearings. Pass = 200 and dated future hearings.")
    house = _http("https://docs.house.gov/Committee/Calendar/ByWeek.aspx",
                  "House side is HTML, not a feed — checking reachability only")
    if house is not None and house.status_code == 200:
        hits = len(re.findall(r"(?i)hearing|markup", house.text))
        print(f"    'hearing|markup' occurrences in the page: {hits}")

    # ---- summary ---------------------------------------------------------
    print("\n" + "=" * 64)
    print("READ THE SAMPLES, NOT THE STATUS CODES. Round 14: a 200 with forty")
    print("perfectly formed, fully timestamped items was 41.9 hours stale.\n")
    for name, verdict in verdicts:
        print(f"  {name}: {verdict}")
    print(f"\n  1 White House: {'answered' if wh else 'no readable feed'}"
          f"{' · newest ' + _age(wh.get('newest')) if wh else ''}")
    print(f"  2 State Dept:  {'answered' if state else 'no readable feed'}"
          f"{' · newest ' + _age(state.get('newest')) if state else ''}")
    if adr is not None:
        print(f"  3 Kraken ADR:  {adr:.2f}% over 14 days — threshold v2 has a "
              f"scale to use")
    print("\nWrite EVERY result into PROJECT_STATE.md §12.2, dead ones "
          "included, with an S0-S8 code. The dead entries are what stop the "
          "same API being rediscovered enthusiastically in six months.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
