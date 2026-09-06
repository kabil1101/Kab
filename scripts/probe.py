"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.

The point is to answer, from an actual Actions runner, the only question that
matters about a candidate: does it respond, and what shape is the response?
Farside is the standing lesson - it is a plain public page that works from a
browser and 403s a datacenter IP, and no amount of reading its documentation
would have revealed that. So: probe, read the output, then write a fetcher
against what actually came back.
"""

from __future__ import annotations

import json
import re

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
    # Round 7. Kabil follows two people and one operation: Fed Chair Warsh,
    # Treasury Secretary Bessent, and Treasury bond buybacks. Question is
    # whether any of that is available as a feed rather than a press page.
    ("fed/press-all", "https://www.federalreserve.gov/feeds/press_all.xml"),
    ("fed/speeches", "https://www.federalreserve.gov/feeds/speeches.xml"),
    ("fed/press-monetary",
     "https://www.federalreserve.gov/feeds/press_monetary.xml"),
    ("fed/testimony", "https://www.federalreserve.gov/feeds/testimony.xml"),
    ("treasury/press-rss", "https://home.treasury.gov/rss/press.xml"),
    ("treasury/news-index", "https://home.treasury.gov/news/press-releases"),
    ("treasurydirect/announced",
     "https://www.treasurydirect.gov/TA_WS/securities/announced?format=json&pagesize=5"),
    ("treasurydirect/buyback-upcoming",
     "https://www.treasurydirect.gov/TA_WS/buybacks/announced?format=json"),
    ("fiscaldata/buybacks",
     "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/buybacks_operations?page[size]=3"),
]

# RSS item fields worth seeing to know whether a feed is usable.
ITEM_RX = re.compile(r"<item>(.*?)</item>", re.S | re.I)
TAG_RX = {t: re.compile(rf"<{t}[^>]*>(.*?)</{t}>", re.S | re.I)
          for t in ("title", "pubDate", "link", "dc:date")}


def show_rss(body: str, limit: int = 5) -> None:
    items = ITEM_RX.findall(body)
    print(f"  RSS: {len(items)} items")
    for raw in items[:limit]:
        bits = []
        for tag, rx in TAG_RX.items():
            m = rx.search(raw)
            if m:
                txt = re.sub(r"<[^>]+>", "", m.group(1))
                txt = " ".join(txt.split())
                if txt:
                    bits.append(f"{tag}={txt[:95]}")
        print(f"    - {' | '.join(bits)}")


def show_json(body: str, limit: int = 3) -> None:
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print("  declared JSON but did not parse")
        return
    if isinstance(data, dict):
        print(f"  JSON object, keys: {sorted(data)[:15]}")
        for key in ("data", "results", "securities"):
            if isinstance(data.get(key), list):
                data = data[key]
                print(f"  .{key}: list of {len(data)}")
                break
    if isinstance(data, list):
        print(f"  list of {len(data)}")
        if data and isinstance(data[0], dict):
            print(f"    record keys: {sorted(data[0])[:25]}")
            for rec in data[:limit]:
                print(f"    - {json.dumps(rec)[:280]}")


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
            low = ctype.lower()
            if "json" in low:
                show_json(r.text)
            elif "xml" in low or "<rss" in r.text[:500].lower():
                show_rss(r.text)
            else:
                print(f"  head: {' '.join(r.text[:220].split())}")
            verdicts.append((name, f"OK {r.status_code}"))
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
