"""Reachability probe for candidate data sources.

Run manually from the Probe Sources workflow. Touches nothing the brief uses.
Probe, read the output, then write a fetcher against what actually came back.
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

# Round 10. The brief missed Treasury's 9 Sep announcement that buybacks go to
# $6bn, because the Fiscal Data set carries completed operations only and
# Treasury publishes no press feed. Round 8 concluded "no feed" and stopped
# there; that conclusion is now known to cost real information, so this round
# goes after the announcement itself rather than the result.
#
# Three routes to test:
#   1. Is the press-release index server-rendered, or a JavaScript shell? If
#      the titles and dates are in the HTML, it is parseable after all.
#   2. Does TreasuryDirect expose buyback announcements under some endpoint
#      shape round 7 did not guess?
#   3. Does Fiscal Data carry an announcements dataset alongside the
#      operations one?
# Round 11. The 9 Sep announcement WAS in the dataset and WAS in the brief -
# as "Buyback 10 Sep · — accepted of — offered", which is worse than absent,
# because it reads as broken data rather than as the most important line in
# the section. total_par_amt_offered is null until the operation runs, so the
# announced MAXIMUM ($6bn) is not in the operations table at all. It is in the
# preliminary announcement, whose filename the table does give us:
# BBPA_20260910174000.xml. This round hunts for that file's base URL.
BBPA = "BBPA_20260910174000.xml"
CANDIDATES = [
    ("xml/td-root", f"https://www.treasurydirect.gov/xml/{BBPA}"),
    ("xml/td-preanre",
     f"https://www.treasurydirect.gov/instit/annceresult/press/preanre/2026/{BBPA}"),
    ("xml/td-annceresult",
     f"https://www.treasurydirect.gov/instit/annceresult/press/preanre/{BBPA}"),
    ("xml/td-buyback-dir",
     f"https://www.treasurydirect.gov/instit/annceresult/buyback/{BBPA}"),
    ("xml/fiscaldata-files",
     f"https://api.fiscaldata.treasury.gov/static-data/buybacks/{BBPA}"),
    # Whatever the answer, confirm what the operations row actually carries
    # for an announced-but-unrun operation, field by field.
    ("fd/announced-row",
     "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1"
     "/accounting/od/buybacks_operations?sort=-operation_date&page[size]=2"),
]

# Words that would prove a press index is server-rendered rather than a shell.
PROOF = ("buyback", "Buyback", "press-releases/sb", "Bessent", "Treasury Announces")


def main() -> int:
    print(f"Probing {len(CANDIDATES)} candidates from an Actions runner\n")
    verdicts = []
    for name, url in CANDIDATES:
        print(f"--- {name}\n    {url}")
        try:
            r = requests.get(url, headers=BROWSER, timeout=TIMEOUT)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAILED {type(exc).__name__}\n")
            verdicts.append((name, "unreachable"))
            continue

        ctype = r.headers.get("content-type", "?")
        print(f"  HTTP {r.status_code} · {ctype} · {len(r.content):,} bytes")
        body = r.text
        if r.ok and "json" in ctype.lower():
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                print("  declared JSON, did not parse")
            else:
                if isinstance(data, dict):
                    print(f"  keys: {sorted(data)[:12]}")
                    rows = data.get("data") or data.get("results")
                else:
                    rows = data if isinstance(data, list) else None
                if isinstance(rows, list):
                    print(f"  {len(rows)} rows")
                    for rec in rows[:3]:
                        print(f"    {json.dumps(rec)[:300]}")
        elif r.ok and name.startswith("xml/"):
            print(f"  RAW:\n{' '.join(body[:1400].split())}")
        elif r.ok:
            hits = [p for p in PROOF if p in body]
            print(f"  server-rendered markers present: {hits or 'NONE'}")
            # Press-release links carry a stable /press-releases/<id> shape.
            links = re.findall(r'href="(/news/press-releases/[a-z0-9]+)"', body)
            uniq = list(dict.fromkeys(links))[:8]
            print(f"  press-release links found: {len(links)} "
                  f"({len(set(links))} unique)")
            for l in uniq:
                print(f"    {l}")
            # Any headline text near those links?
            for m in list(re.finditer(
                    r'href="/news/press-releases/[a-z0-9]+"[^>]*>([^<]{10,140})<',
                    body))[:6]:
                print(f"    title: {' '.join(m.group(1).split())}")
            # Dates?
            for m in list(re.finditer(
                    r'(\d{1,2}/\d{1,2}/20\d{2}|20\d{2}-\d{2}-\d{2}|'
                    r'(?:January|February|March|April|May|June|July|August|'
                    r'September|October|November|December)\s+\d{1,2},\s+20\d{2})',
                    body))[:6]:
                print(f"    date-ish: {m.group(1)}")
        else:
            print(f"  body: {' '.join(body[:160].split())}")
        verdicts.append((name, f"HTTP {r.status_code}"))
        print()

    print("=" * 60)
    for name, verdict in verdicts:
        print(f"{verdict:<16} {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
