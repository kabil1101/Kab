"""Offline tests for the pure logic: timezone handling, max pain, flow runs,
and end-to-end rendering with both healthy and fully-degraded inputs.

No network. Everything here must pass before the workflow is trusted.
"""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import render  # noqa: E402
import sources  # noqa: E402

LISBON = ZoneInfo("Europe/Lisbon")
ET = ZoneInfo("America/New_York")
failures = []


def check(name, got, want):
    if got != want:
        failures.append(f"{name}: got {got!r}, want {want!r}")
    else:
        print(f"  ok  {name}")


def check_true(name, cond, detail=""):
    if not cond:
        failures.append(f"{name}: {detail}")
    else:
        print(f"  ok  {name}")


print("\n-- ET -> Lisbon conversion across DST mismatch windows --")
# The US and the EU switch on different dates, so the ET->Lisbon gap is not
# constant. Parsing the offset out of the ISO string must handle all of it.
for label, iso, want_lis_hour, want_gap in [
    ("August (both on DST)",      "2026-08-21T08:30:00-04:00", 13, 5),
    ("mid-March (US on, EU off)", "2026-03-16T08:30:00-04:00", 12, 4),
    ("late-Oct (EU off, US on)",  "2026-10-28T08:30:00-04:00", 12, 4),
    ("December (both off)",       "2026-12-15T08:30:00-05:00", 13, 5),
]:
    dt = datetime.fromisoformat(iso)
    lis = dt.astimezone(LISBON)
    gap = int((lis.utcoffset() - dt.utcoffset()).total_seconds() // 3600)
    check(f"{label} hour", lis.hour, want_lis_hour)
    check(f"{label} gap", gap, want_gap)

print("\n-- ForexFactory feed parsing --")
rows = [
    {"title": "Flash Manufacturing PMI", "country": "USD",
     "date": "2026-08-21T09:45:00-04:00", "impact": "High",
     "forecast": "52.0", "previous": "51.8"},
    {"title": "Crude Oil Inventories", "country": "USD",
     "date": "2026-08-21T10:30:00-04:00", "impact": "Low",
     "forecast": "", "previous": "-1.2M"},
    {"title": "Retail Sales m/m", "country": "CAD",
     "date": "2026-08-21T08:30:00-04:00", "impact": "Medium",
     "forecast": "0.4%", "previous": "0.1%"},
    {"title": "FOMC Member Speaks", "country": "USD",
     "date": "2026-08-24T14:00:00-04:00", "impact": "High",
     "forecast": "", "previous": ""},
]
parsed = sources._parse_ff(rows, set())
check("parsed count", len(parsed), 4)
check("USD PMI lands 14:45 LIS", parsed[0]["dt_lis"].strftime("%H:%M"), "14:45")

# Duplicate suppression across the two weekly feeds.
seen = set()
sources._parse_ff(rows, seen)
check("dedupe on second feed", len(sources._parse_ff(rows, seen)), 0)

today = date(2026, 8, 21)
todays = render.select_today(parsed, today)
check("today selection keeps High+Medium+oil Low", len(todays), 3)
check_true("crude oil inventories retained despite Low impact",
           any("Crude Oil" in e["title"] for e in todays))
fwd = render.select_forward(parsed, today)
check("forward view finds Monday High", len(fwd), 1)

print("\n-- max pain --")
# Heavy puts at 110, light calls at 100: settling at 110 pays out least.
by_strike = {100.0: {"C": 1.0}, 110.0: {"P": 10.0}}
check("max pain picks the heavy-put strike", sources._max_pain(by_strike), 110.0)
# Symmetric book settles at the strike that minimises total intrinsic.
sym = {90.0: {"C": 5.0, "P": 1.0}, 100.0: {"C": 1.0, "P": 1.0}, 110.0: {"P": 5.0}}
mp = sources._max_pain(sym)
check_true("symmetric book resolves to an interior strike", mp == 100.0, f"got {mp}")

print("\n-- Deribit monthly detection (last Friday) --")
check("2026-08-28 is a monthly", sources._is_monthly(date(2026, 8, 28)), True)
check("2026-08-21 is not", sources._is_monthly(date(2026, 8, 21)), False)
check("2026-12-25 is a monthly", sources._is_monthly(date(2026, 12, 25)), True)

print("\n-- Farside negative parsing --")
check("parenthesised is negative", sources._money("(123.4)"), -123.4)
check("comma thousands", sources._money("1,234.5"), 1234.5)
check("dash is None", sources._money("-"), None)

print("\n-- flow run direction --")
flip = render._run_note([10.0, 20.0, 30.0, 40.0, -5.0])
check_true("sign flip after 3+ sessions is flagged", "FLAG" in flip, flip)
steady = render._run_note([10.0, 20.0, 30.0, 40.0, 50.0])
check_true("steady run is not flagged", "FLAG" not in steady, steady)

print("\n-- flow run direction (regression) --")
check_true("3-day inflow then outflow flags",
           "FLAG" in render._run_note([10.0, 20.0, 30.0, -5.0]))
check_true("steady 5-day inflow does not flag",
           "FLAG" not in render._run_note([10.0, 20.0, 30.0, 40.0, 50.0]))
check_true("steady 5-day outflow does not flag",
           "FLAG" not in render._run_note([-1.0, -2.0, -3.0, -4.0, -5.0]))
check_true("single flip after only 2 sessions does not flag",
           "FLAG" not in render._run_note([10.0, 20.0, -5.0]))
check_true("short series degrades cleanly",
           render._run_note([5.0]) == "run direction unavailable")

print("\n-- end-to-end render: healthy inputs --")
now = datetime(2026, 8, 21, 9, 30, tzinfo=LISBON)
healthy = {
    "now": now,
    "calendar": {"ok": True, "error": None,
                 "data": {"events": parsed, "next_week_error": None,
                          "source": "ff"}},
    "crypto": {"ok": True, "error": None, "data": {"source": "kraken", "pairs": [
        {"symbol": "BTC", "last": 76800.0, "day_open": 75000.0,
         "pct_since_utc_midnight": 2.4, "high_24h": 79500.0,
         "low_24h": 74100.0, "vol_24h": 1234.5, "vwap_24h": 77000.0}]}},
    "fear_greed": {"ok": True, "error": None, "data": {
        "today": {"value": 72, "classification": "Greed",
                  "at": datetime(2026, 8, 21, tzinfo=timezone.utc)},
        "week_ago": {"value": 41, "classification": "Fear",
                     "at": datetime(2026, 8, 14, tzinfo=timezone.utc)},
        "source": "alternative.me"}},
    "flows_btc": {"ok": True, "error": None, "data": {
        "latest_date": date(2026, 8, 20), "latest_total": 606.3,
        "recent": [{"date": date(2026, 8, 20), "total": 606.3,
                    "ibit": 503.0, "fbtc": 64.7, "etha": None}],
        "source": "farside"}},
    "flows_eth": {"ok": False, "error": "HTTP 503", "data": None},
    "options_btc": {"ok": True, "error": None, "data": {
        "currency": "BTC", "underlying": 76800.0,
        "nearest": {"expiry": date(2026, 8, 21), "max_pain": 70000.0,
                    "top_call_strike": 80000.0, "top_call_oi": 900.0,
                    "top_put_strike": 70000.0, "top_put_oi": 800.0,
                    "put_call_oi_ratio": 0.83, "total_oi": 5000.0},
        "monthly": {"expiry": date(2026, 8, 28), "max_pain": 72000.0,
                    "top_call_strike": 85000.0, "top_call_oi": 1200.0,
                    "top_put_strike": 68000.0, "top_put_oi": 1100.0,
                    "put_call_oi_ratio": 0.91, "total_oi": 9000.0},
        "source": "deribit"}},
    "cross_asset": {"ok": True, "error": None, "data": {
        "quotes": {"DXY": {"last": 98.67, "pct_change": -0.14, "as_of": now},
                   "US 10Y": {"last": 4.70, "pct_change": 0.3, "as_of": now}},
        "errors": {"VIX": "timeout"}, "source": "yahoo"}},
    "global_mcap": {"ok": True, "error": None, "data": {
        "total_mcap_usd": 2.61e12, "mcap_change_24h_pct": 3.4,
        "btc_dominance": 58.2, "eth_dominance": 9.1, "source": "coingecko"}},
}
md, html = render.build(healthy)
check_true("markdown has a title", md.startswith("# MARKET BRIEF"))
check_true("BTC price rendered", "76,800" in md)
check_true("pct labelled since 00:00 UTC", "since 00:00 UTC" in md)
check_true("F&G 7-day delta shown", "+31" in md)
check_true("failed sub-step reported", "flows_eth" in md and "Degraded" in md)
check_true("max pain rendered", "70,000" in md)
check_true("alternative.me attribution present", "alternative.me" in md)
check_true("no literal markdown bold leaked into HTML", "**" not in html)
check_true("html is a complete document",
           html.startswith("<html>") and html.endswith("</html>"))
check_true("cross-asset partial failure surfaced", "VIX" in html)
# NYSE open on 21 Aug 2026: 09:30 EDT -> 14:30 Lisbon.
check_true("NYSE open converted to 14:30 LIS", "14:30" in md, md)

print("\n-- end-to-end render: every source down --")
dead = {"now": now}
for k in ("calendar", "crypto", "fear_greed", "flows_btc", "flows_eth",
          "options_btc", "cross_asset", "global_mcap"):
    dead[k] = {"ok": False, "error": "EGRESS_BLOCKED", "data": None}
md2, html2 = render.build(dead)
check_true("degraded brief still renders", md2.startswith("# MARKET BRIEF"))
check_true("degraded brief names every failure",
           all(k in md2 for k in ("calendar", "crypto", "flows_btc")))
check_true("degraded brief still emits risk windows", "NYSE cash open" in md2)
check_true("degraded html still closes", html2.endswith("</html>"))
check_true("no crash-y placeholder numbers", "0%" not in md2)


print("\n-- run guard: which cron slot owns the day --")
import os as _os  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import main as brief_main  # noqa: E402


def guard(schedule, when, force=""):
    _os.environ["BRIEF_SCHEDULE"] = schedule
    _os.environ["FORCE_RUN"] = force
    try:
        return brief_main.should_run(when)
    finally:
        _os.environ.pop("BRIEF_SCHEDULE", None)
        _os.environ.pop("FORCE_RUN", None)


summer = datetime(2026, 8, 21, 9, 25, tzinfo=LISBON)   # WEST, UTC+1
winter = datetime(2026, 12, 11, 9, 25, tzinfo=LISBON)  # WET,  UTC+0
EARLY, LATE = "25 8 * * 1-5", "25 9 * * 1-5"

check("summer: early slot runs", guard(EARLY, summer), True)
check("summer: late slot skips", guard(LATE, summer), False)
check("winter: early slot skips", guard(EARLY, winter), False)
check("winter: late slot runs", guard(LATE, winter), True)
check("manual dispatch always runs", guard("", summer), True)
check("FORCE_RUN overrides", guard(LATE, summer, force="1"), True)
check("garbage schedule fails open", guard("not-a-cron", summer), True)

print("\n-- compact error reasons --")
import requests as _rq  # noqa: E402


class _R:
    status_code = 503


check("http status surfaces", sources._reason(
    _rq.HTTPError(response=_R())), "HTTP 503")
check("timeout named", sources._reason(_rq.Timeout()), "timeout")
check("connection error named", sources._reason(_rq.ConnectionError()),
      "connection failed")
check_true("error text stays short enough for an email body",
           len(sources._reason(_rq.ConnectionError("x" * 500))) < 40)

print("\n-- forward feed: dead vs genuinely empty --")
dead_fwd = dict(healthy)
dead_fwd["calendar"] = {"ok": True, "error": None, "data": {
    "events": [e for e in parsed if e["dt_lis"].date() == today],
    "next_week_error": "nfs.faireconomy.media: HTTP 403", "source": "ff"}}
md3, _ = render.build(dead_fwd)
check_true("dead forward feed is not reported as 'none scheduled'",
           "None scheduled" not in md3, md3)
check_true("dead forward feed names the failure", "HTTP 403" in md3)

empty_fwd = dict(healthy)
empty_fwd["calendar"] = {"ok": True, "error": None, "data": {
    "events": [e for e in parsed if e["dt_lis"].date() == today],
    "next_week_error": None, "source": "ff"}}
md4, _ = render.build(empty_fwd)
check_true("genuinely empty forward feed still says none scheduled",
           "None scheduled" in md4)

print("\n-- app password whitespace tolerance --")
_os.environ["GMAIL_USER"] = "  kabil.dh@gmail.com  "
_os.environ["GMAIL_APP_PASSWORD"] = "abcd efgh ijkl mnop"
try:
    brief_main.send_email("t", "t", "<p>t</p>")
except Exception as _e:
    msg = str(_e)
    check_true("spaced app password is not rejected as missing",
               "missing repository secret" not in msg, msg)
finally:
    _os.environ.pop("GMAIL_USER", None)
    _os.environ.pop("GMAIL_APP_PASSWORD", None)

_os.environ["GMAIL_USER"] = "u@example.com"
_os.environ["GMAIL_APP_PASSWORD"] = "   "
try:
    brief_main.send_email("t", "t", "<p>t</p>")
    failures.append("whitespace-only password should still count as missing")
except Exception as _e:
    check_true("whitespace-only password still counts as missing",
               "GMAIL_APP_PASSWORD" in str(_e), str(_e))
finally:
    _os.environ.pop("GMAIL_USER", None)
    _os.environ.pop("GMAIL_APP_PASSWORD", None)

print("\n-- analyst digest --")
import analyst  # noqa: E402  (imports `anthropic` lazily, inside analyse())

dig = analyst.digest(healthy)
check_true("digest carries the real BTC price", "76,800" in dig, dig[:200])
check_true("digest labels the UTC-midnight window",
           "since 00:00 UTC" in dig)
check_true("digest states a failed source as unavailable",
           "UNAVAILABLE" in dig and "HTTP 503" in dig)
check_true("digest carries max pain", "70,000" in dig)
check_true("digest carries the F&G 7-day comparison", "7 days ago 41" in dig)
check_true("digest is timezone-anchored", "Lisbon" in dig)

dead_dig = analyst.digest(dead)
check_true("all-blind digest still renders", "AS OF:" in dead_dig)
check_true("all-blind digest marks every section unavailable",
           dead_dig.count("UNAVAILABLE") >= 6, dead_dig)
check_true("all-blind digest invents no figures",
           "$" not in dead_dig.replace("AS OF:", ""), dead_dig)

check_true("quarantined sources are unreachable by the analyst",
           not any(d in analyst.ALLOWED_DOMAINS for d in
                   ("coinglass.com", "optioncharts.io", "cmegroup.com",
                    "theblock.co", "coinalyze.net")))
check_true("farside is reachable by the analyst (the standing gap)",
           "farside.co.uk" in analyst.ALLOWED_DOMAINS)
check("analyst uses Opus 5", analyst.MODEL, "claude-opus-5")

print("\n-- analysis section rendering --")
with_an = dict(healthy)
with_an["analysis"] = {"ok": True, "error": None, "data": (
    "### Read\nBTC is **pinned** to max pain at $70,000.\n\n"
    "### Watch\n- 14:45 LIS US Flash PMI\n- 21:00 LIS close")}
md5, html5 = render.build(with_an)
check_true("analysis appears in the markdown", "## ANALYSIS" in md5)
check_true("analysis precedes the data", md5.index("## ANALYSIS")
           < md5.index("## THE SETUP"))
check_true("analysis headings become h3", "<h3>Read</h3>" in html5, html5[:400])
check_true("analysis bullets become li", "<li>14:45 LIS US Flash PMI</li>" in html5)
check_true("analysis bold becomes strong", "<strong>pinned</strong>" in html5)
check_true("no markdown leaks into analysis html",
           "**" not in html5 and "###" not in html5)

print("\n-- a failed analysis never costs the brief --")
no_an = dict(healthy)
no_an["analysis"] = {"ok": False, "error": "missing repository secret: "
                                           "ANTHROPIC_API_KEY", "data": None}
md6, html6 = render.build(no_an)
check_true("brief still renders without analysis", md6.startswith("# MARKET BRIEF"))
check_true("data sections survive", "76,800" in md6)
check_true("missing analysis is stated, not hidden",
           "Analysis unavailable" in md6 and "ANTHROPIC_API_KEY" in md6)
check_true("failed analysis is listed as degraded", "analysis" in md6.split(
    "Degraded this run:")[-1])

print("\n-- model output cannot inject markup --")
evil = dict(healthy)
evil["analysis"] = {"ok": True, "error": None,
                    "data": "### <script>alert(1)</script>\nplain <b>text</b>"}
_, html7 = render.build(evil)
check_true("script tag is escaped", "<script>" not in html7)
check_true("raw html in model output is escaped", "<b>text</b>" not in html7)
check_true("escaped form is present", "&lt;script&gt;" in html7)

print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("All checks passed.")
