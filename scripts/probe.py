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

FEEDS = {
    "speeches": "https://www.federalreserve.gov/feeds/speeches.xml",
    "testimony": "https://www.federalreserve.gov/feeds/testimony.xml",
    "press_monetary":
        "https://www.federalreserve.gov/feeds/press_monetary.xml",
}

# Round 9, the last one. Rounds 7-8 proved the Fed feeds answer and that their
# titles are "Speaker, Subject" - "Warsh, In Our Time" - which is all the
# filtering needs. What they did NOT show is a date or a link on any item:
# Treasury's feed printed pubDate and link, the Fed's printed neither. Either
# the Fed uses different tags or its items carry no date at all, and a
# "recent remarks" section cannot be built on a guess about which.
#
# So: dump one raw item per feed, verbatim, and read the tags off it.


def main() -> int:
    import re
    for name, url in FEEDS.items():
        print(f"--- {name}\n    {url}")
        try:
            r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {type(exc).__name__}\n")
            continue
        print(f"  HTTP {r.status_code} · {len(r.content):,} bytes")
        body = r.text
        # The channel header names the namespaces the items use.
        print(f"  channel head: {' '.join(body[:420].split())}")
        m = re.search(r"<item[ >].*?</item>", body, re.S | re.I)
        if not m:
            print("  no <item> found\n")
            continue
        raw = " ".join(m.group(0).split())
        print(f"  first item verbatim:\n    {raw[:900]}")
        print(f"  tags present: {sorted(set(re.findall(r'<([a-zA-Z:]+)[ />]', m.group(0))))}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
