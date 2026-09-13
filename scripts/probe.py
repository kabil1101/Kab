"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

TIMEOUT = 25
BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Round 14. Two questions, and they are asked in this order deliberately.
#
# 1. FRED, for release ACTUALS. The 09:20 brief can only ever print a
#    forecast, because sources.py:143 is right - ForexFactory is schedule-only
#    and carries no `actual` field. A second edition at 14:00 Lisbon (09:00 ET,
#    thirty minutes after the 08:30 ET prints) is worth sending only if it can
#    say what a number actually came in at.
#
#    FRED needs a free API key, which means Kabil has to go and sign up. That
#    is his time, and it would be wasted if FRED turns out to refuse datacenter
#    IPs the way Farside, Binance and CME all did. So probe with a DELIBERATELY
#    INVALID key first: a 400 saying the key is unregistered proves the host
#    answers us and auth is the only barrier, while a 403 or a timeout means
#    excluded and nobody signs up for anything.
#
# 2. The four news accounts Kabil follows on X, probed at their PRIMARY
#    sources rather than through X. X killed its free tier in February 2026
#    ($0.005/read, no free option for new developers) and Nitter is under
#    cease-and-desist, so X itself fails D2 and the reachability bar at once.
#    But three of the four accounts are relays of sites that publish their own
#    feeds - which is §12.4a exactly: name the route that failed, then ask what
#    else carries the same fact.
#
#    For a feed, HTTP 200 is not the answer. §3.7 already cost this project a
#    source that answered 200 with careers pages. What matters here is whether
#    items carry a parseable timestamp and HOW FAR BACK the feed reaches: an
#    "everything since the last brief" section needs ~24h of history for the
#    morning edition. A feed holding 10 items spanning two busy hours cannot
#    support the design, however healthy its status code.
FRED_BAD_KEY = "0123456789abcdef0123456789abcdef"

CANDIDATES = [
    # --- FRED: reachability before signup -----------------------------------
    ("fred/observations-badkey",
     "https://api.stlouisfed.org/fred/series/observations"
     f"?series_id=CPIAUCSL&api_key={FRED_BAD_KEY}&file_type=json&limit=3"),
    ("fred/releases-badkey",
     "https://api.stlouisfed.org/fred/releases"
     f"?api_key={FRED_BAD_KEY}&file_type=json&limit=3"),

    # --- news primaries: the four X accounts, at source ----------------------
    ("zerohedge/feedburner", "https://feeds.feedburner.com/zerohedge/feed"),
    ("zerohedge/fullrss2", "https://www.zerohedge.com/fullrss2.xml"),
    ("watcherguru/feed", "https://watcher.guru/news/feed"),
    ("watcherguru/rootfeed", "https://watcher.guru/feed"),
    ("financialjuice/home", "https://www.financialjuice.com/"),
    # @DeItaone relays a Bloomberg terminal verbatim; there is no free primary,
    # so these are the substitutes. A daily brief is already hours behind, so
    # the latency they give up against a terminal costs this reader nothing.
    ("cnbc/topnews", "https://search.cnbc.com/rs/search/combinedcms/view.xml"
                     "?partnerId=wrss01&id=100003114"),
    ("marketwatch/topstories",
     "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
    ("yahoo/finance-news",
     "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"),
]


def _stamp(text):
    """A datetime from an RSS/Atom date string, or None."""
    if not text:
        return None
    text = text.strip()
    try:
        d = parsedate_to_datetime(text)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _feed_report(body: bytes) -> bool:
    """Print item count, titles and the window the feed covers. True if parsed."""
    # BOM and leading whitespace both break ElementTree, and the Fed feeds
    # already taught this project that lesson (§12.2).
    raw = body.lstrip(b"\xef\xbb\xbf").lstrip()
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"  not parseable XML: {exc}")
        return False

    items = root.findall(".//item") or root.findall(
        ".//{http://www.w3.org/2005/Atom}entry")
    if not items:
        print("  parsed, but zero items")
        return False

    def _txt(el, *names):
        for n in names:
            found = el.find(n)
            if found is not None and (found.text or "").strip():
                return found.text.strip()
        return ""

    stamps = []
    for it in items:
        s = _stamp(_txt(it, "pubDate", "date", "{http://purl.org/dc/elements/1.1/}date",
                        "{http://www.w3.org/2005/Atom}updated",
                        "{http://www.w3.org/2005/Atom}published"))
        if s:
            stamps.append(s)

    print(f"  items: {len(items)} · with a parseable timestamp: {len(stamps)}")
    for it in items[:3]:
        t = _txt(it, "title", "{http://www.w3.org/2005/Atom}title")
        print(f"    - {' '.join(t.split())[:110]}")

    if not stamps:
        print("  NO USABLE TIMESTAMPS — cannot support a 'since last brief' window")
        return True
    newest, oldest = max(stamps), min(stamps)
    span_h = (newest - oldest).total_seconds() / 3600
    age_h = (datetime.now(timezone.utc) - newest).total_seconds() / 3600
    print(f"  newest {newest:%Y-%m-%d %H:%M %Z} (age {age_h:.1f}h) · "
          f"oldest {oldest:%Y-%m-%d %H:%M %Z}")
    print(f"  window covered: {span_h:.1f}h "
          f"{'— ENOUGH for a 24h look-back' if span_h >= 24 else '— TOO SHORT for 24h'}")
    return True


def main() -> int:
    print(f"Round 14 · probing {len(CANDIDATES)} candidates from an Actions runner\n")
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

        if name.startswith("fred/"):
            # The body is the whole point: which barrier answered us?
            print(f"  body: {' '.join(r.text[:300].split())}")
            if r.status_code == 400 and "api_key" in r.text.lower():
                print("  => REACHABLE. Auth is the only barrier — a key is worth getting.")
            elif r.status_code in (403, 451):
                print("  => BLOCKED at the edge. Do not sign up; this is Farside again.")
        elif "xml" in ctype.lower() or "rss" in ctype.lower() or r.content[:200].lstrip().startswith(b"<?xml"):
            _feed_report(r.content)
        elif r.ok:
            head = " ".join(r.text[:200].split())
            print(f"  head: {head}")
            # Does the page advertise a feed we could use instead?
            links = re.findall(
                r'<link[^>]+type=["\']application/(?:rss|atom)\+xml["\'][^>]*>',
                r.text, re.I)[:3]
            for l in links:
                print(f"  advertises feed: {' '.join(l.split())[:160]}")
            if not links:
                print("  no RSS/Atom <link> advertised in the HTML head")
        else:
            print(f"  body: {' '.join(r.text[:200].split())}")

        verdicts.append((name, f"HTTP {r.status_code}"))
        print()

    print("=" * 64)
    for name, verdict in verdicts:
        print(f"{verdict:<16} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
