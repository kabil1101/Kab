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
# The default response omits effective_on entirely, which is the only field
# that makes a document forward-looking. It has to be asked for by name.
FIELDS = ("&fields[]=title&fields[]=type&fields[]=effective_on"
          "&fields[]=publication_date&fields[]=agencies&fields[]=html_url"
          "&fields[]=comments_close_on")

CANDIDATES = [
    # Round 5: pin the exact queries the policy-calendar fetcher will use.
    # Round 4 proved the API answers; it did not prove it answers usefully.
    ("fr/presdocu-future-effective",
     f"{FR}?per_page=20&order=effective_date{FIELDS}"
     "&conditions[type][]=PRESDOCU"
     "&conditions[effective_date][gte]=2026-09-06"),
    ("fr/trade-terms-future-effective",
     f"{FR}?per_page=20&order=effective_date{FIELDS}"
     "&conditions[effective_date][gte]=2026-09-06"
     "&conditions[term]=tariff OR sanctions OR \"export control\" OR quota"),
    ("fr/comments-closing",
     f"{FR}?per_page=10&order=newest{FIELDS}"
     "&conditions[comments_close_on][gte]=2026-09-06"
     "&conditions[term]=tariff OR sanctions"),
    ("fr/presdocu-recent-30d",
     f"{FR}?per_page=20&order=newest{FIELDS}"
     "&conditions[type][]=PRESDOCU"
     "&conditions[publication_date][gte]=2026-08-06"),
    ("fr/tariff-recent",
     f"{FR}?per_page=10&order=newest{FIELDS}"
     "&conditions[term]=tariff"
     "&conditions[publication_date][gte]=2026-08-01"),
]

# Print every record's headline fields, not just the first one: the question
# these queries answer is "how much of this is signal", and one record cannot
# say.
TABLE_KEYS = ("effective_on", "comments_close_on", "publication_date", "type",
              "title")

DEEP = True   # dump full structure for these, not just a one-line summary


# Substrings worth surfacing when a page turns out to be an app shell: they
# point at the data the page itself loads.
DATA_HINTS = (".csv", ".json", "/api/", "__NEXT_DATA__", "sosovalue",
              "farside", "netflow", "net_flow", "totalNetInflow")


def hunt(body: str) -> list[str]:
    """Candidate data URLs and markers embedded in an app-shell page."""
    import re
    found = []
    for m in re.finditer(r'["\'(]([^"\'()\s]{4,160}?\.(?:csv|json))["\')]', body,
                         re.I):
        found.append(m.group(1))
    for m in re.finditer(r'["\'(](/api/[^"\'()\s]{2,120})["\')]', body, re.I):
        found.append(m.group(1))
    seen, out = set(), []
    for f in found:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out[:15]


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
            if DEEP and "json" in ctype.lower():
                try:
                    data = json.loads(r.text)
                except json.JSONDecodeError:
                    data = None
                if isinstance(data, dict) and isinstance(data.get("results"),
                                                         list):
                    print(f"  count={data.get('count')} "
                          f"returned={len(data['results'])}")
                    for rec in data["results"]:
                        bits = []
                        for k in TABLE_KEYS:
                            v = rec.get(k)
                            if k == "title" and v:
                                v = " ".join(str(v).split())[:90]
                            bits.append(f"{k}={v}")
                        ag = [a.get("name") for a in (rec.get("agencies") or [])
                              if isinstance(a, dict)]
                        print(f"    - {' · '.join(bits)}"
                              f"{' · agencies=' + str(ag[:2]) if ag else ''}")
            if "json" not in ctype.lower():
                urls = hunt(r.text)
                if urls:
                    print("  embedded data references:")
                    for u in urls:
                        print(f"    {u}")
                present = [h for h in DATA_HINTS if h.lower() in r.text.lower()]
                if present:
                    print(f"  markers present: {present}")
            print(f"  head: {' '.join(r.text[:200].split())}")
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
