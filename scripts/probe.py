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

FR = "https://www.federalregister.gov/api/v1/documents.json"

# Round 6. Rounds 4-5 settled the structured question: the Federal Register
# never populates effective_on for presidential documents (0 of 21), and
# comments_close_on is not a filterable condition (HTTP 400). So the forward
# dates that matter - "duties apply to goods entered on or after 14 October" -
# exist only inside the prose of the document.
#
# This round asks whether they can be pulled out of that prose reliably enough
# to print in a brief. It fetches the raw text of recent presidential documents
# and every calendar date in them, with the words around each one, so the
# classifier is written against real sentences instead of imagined ones.

RECENT = (f"{FR}?per_page=40&order=newest"
          "&fields[]=title&fields[]=publication_date&fields[]=document_number"
          "&fields[]=raw_text_url&fields[]=html_url&fields[]=type"
          "&conditions[type][]=PRESDOCU"
          "&conditions[publication_date][gte]=2026-07-01")

# Market-relevant is a judgement, and this is the judgement: things that move
# prices are trade barriers, sanctions, export controls, energy and emergency
# powers. Renamings of lakes and national awareness months are not.
MARKET_WORDS = (
    "tariff", "duty", "duties", "import", "export", "trade", "sanction",
    "embargo", "quota", "steel", "aluminum", "semiconductor", "chip",
    "critical mineral", "energy", "oil", "emergency", "china", "section 232",
    "section 301", "currency", "crypto", "digital asset",
)

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")
DATE_RX = rf"(?:{MONTHS})\s+\d{{1,2}},\s+20\d{{2}}"

# Words that turn a date in the text into a date worth counting down to.
CUES = ("effective", "on or after", "beginning", "commencing", "shall take",
        "expire", "terminate", "no later than", "until", "through",
        "entered for consumption", "withdrawn from warehouse")


def relevant(title: str) -> bool:
    low = title.lower()
    return any(w in low for w in MARKET_WORDS)


def main() -> int:
    import re
    print("Round 6: can effective dates be read out of the prose?\n")
    r = requests.get(RECENT, headers=BROWSER, timeout=TIMEOUT)
    print(f"index: HTTP {r.status_code}")
    if not r.ok:
        return 1
    docs = r.json().get("results") or []
    hits = [d for d in docs if relevant(d.get("title") or "")]
    print(f"{len(docs)} presidential documents since 01 Jul; "
          f"{len(hits)} look market-relevant\n")

    for d in hits:
        print(f"--- {d['publication_date']} · {d['title'][:95]}")
        print(f"    {d.get('html_url')}")
        url = d.get("raw_text_url")
        if not url:
            print("    no raw_text_url\n")
            continue
        try:
            txt = requests.get(url, headers=BROWSER, timeout=TIMEOUT).text
        except Exception as exc:  # noqa: BLE001
            print(f"    raw text FAILED {type(exc).__name__}\n")
            continue
        flat = " ".join(txt.split())
        print(f"    {len(flat):,} chars")
        seen = set()
        for m in re.finditer(DATE_RX, flat):
            before = flat[max(0, m.start() - 130):m.start()].lower()
            cue = [c for c in CUES if c in before]
            key = (m.group(0), tuple(cue))
            if key in seen:
                continue
            seen.add(key)
            mark = "CUE" if cue else "   "
            print(f"    [{mark}] {m.group(0)}  <=  ...{flat[max(0, m.start()-110):m.start()]}")
            if cue:
                print(f"            cues: {cue}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
