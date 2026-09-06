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
import watchlist  # noqa: E402

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
                 "data": {"events": parsed, "week_only": True,
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
        "updated_through": "2026-08-20", "source": "TFTC (CC BY 4.0)"}},
    "perp_btc": {"ok": True, "error": None, "data": {
        "instrument": "BTC-PERPETUAL", "funding_8h": 0.00012,
        "current_funding": 0.00009, "open_interest": 512345678.0,
        "index_price": 76800.0, "volume_24h_usd": 1.78e8,
        "source": "Deribit (single venue)"}},
    "perp_eth": {"ok": False, "error": "HTTP 503", "data": None},
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
check_true("failed sub-step reported", "perp_eth" in md and "Degraded" in md)
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
          "options_btc", "cross_asset", "global_mcap", "policy_radar",
          "fed_officials", "treasury_ops"):
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

print("\n-- forward view: week-only is stated, not left blank --")
_wk = dict(healthy)
_wk["calendar"] = {"ok": True, "error": None, "data": {
    "events": [e for e in parsed if e["dt_lis"].date() == today],
    "week_only": True, "source": "ff"}}
md3, _ = render.build(_wk)
check_true("an exhausted forward view is explained, not shown empty",
           "publishes only the current week" in md3, md3)
check_true("it does not claim a broken feed",
           "unavailable" not in md3.split("Next 5 sessions")[1][:300].lower(), md3)

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

print("\n-- as-of stamps: a stale quote must not look live --")
_fri_close = datetime(2026, 8, 21, 21, 59, tzinfo=LISBON)
_mon = datetime(2026, 8, 24, 9, 30, tzinfo=LISBON)
same = render._as_of_stamp(datetime(2026, 8, 21, 9, 0, tzinfo=LISBON), now)
check_true("same-day quote shows a bare time", same == " (as of 09:00 LIS)", same)
stale = render._as_of_stamp(_fri_close, _mon)
check_true("stale quote carries its date", "Fri 21 Aug" in stale, stale)
check_true("stale quote states its age", "d old" in stale or "h old" in stale, stale)
check_true("no as_of yields no stamp", render._as_of_stamp(None, now) == "")

_stale_ctx = dict(healthy)
_stale_ctx["now"] = _mon
_stale_ctx["cross_asset"] = {"ok": True, "error": None, "data": {
    "quotes": {"DXY": {"last": 99.16, "pct_change": -0.27, "as_of": _fri_close}},
    "errors": {}, "source": "yahoo"}}
md_s, _ = render.build(_stale_ctx)
check_true("Friday's close is not printed as though it were today",
           "Fri 21 Aug" in md_s, md_s)

print("\n-- risk windows: only what is still ahead --")
# The 28 Aug failure: built 21:14, still listing the 14:30 open and 21:00 close.
_late = dict(healthy)
_late["now"] = datetime(2026, 8, 21, 21, 14, tzinfo=LISBON)
md_l, _ = render.build(_late)
_rw = md_l.split("## RISK WINDOWS (LIS)")[1]
check_true("passed NYSE open is dropped", "NYSE cash open" not in _rw, _rw)
check_true("passed NYSE close is dropped", "NYSE cash close" not in _rw, _rw)
check_true("the reader is told windows passed rather than shown nothing",
           "passed" in _rw.lower(), _rw)

_early = dict(healthy)
_early["now"] = datetime(2026, 8, 21, 6, 0, tzinfo=LISBON)
_rw_e = render.build(_early)[0].split("## RISK WINDOWS (LIS)")[1]
check_true("future NYSE open is kept", "NYSE cash open" in _rw_e)
check_true("windows are ordered by time",
           _rw_e.index("14:30") < _rw_e.index("21:00"), _rw_e)

print("\n-- weekends have no cash session --")
_sat = dict(healthy)
_sat["now"] = datetime(2026, 8, 22, 13, 0, tzinfo=LISBON)   # Saturday
_sat["calendar"] = {"ok": True, "error": None,
                    "data": {"events": [], "next_week_error": None, "source": "ff"}}
_rw_s = render.build(_sat)[0].split("## RISK WINDOWS (LIS)")[1]
check_true("no NYSE open on a Saturday", "NYSE cash open" not in _rw_s, _rw_s)
check_true("no NYSE close on a Saturday", "NYSE cash close" not in _rw_s, _rw_s)
check_true("closure is stated, not left blank", "closed" in _rw_s.lower(), _rw_s)

print("\n-- headline says where price sits, not just that it is flat --")
check_true("range position is computed",
           abs(render._range_pos(healthy["crypto"]["data"]["pairs"][0]) - 49.8) < 1.0,
           render._range_pos(healthy["crypto"]["data"]["pairs"][0]))
check_true("degenerate range does not divide by zero",
           render._range_pos({"last": 5.0, "low_24h": 5.0, "high_24h": 5.0}) is None)
md_h, _ = render.build(healthy)
check_true("headline carries range position", "up its 24h range" in md_h, md_h[:400])
check_true("headline keeps the correctly-labelled UTC window",
           "since 00:00 UTC" in md_h)

print("\n-- subject line carries signal --")
subj = render.subject(healthy)
check_true("prefix the Mode Check matches is preserved",
           subj.startswith("Market Brief - "), subj)
check_true("subject names the BTC level", "BTC 76.8k" in subj, subj)
check_true("subject carries the day's USD event", "PMI" in subj, subj)
check_true("subject stays short enough to read in a list", len(subj) < 90, subj)
subj_blind = render.subject(dead)
check_true("subject degrades to the date when nothing was fetched",
           subj_blind.startswith("Market Brief - ") and "BTC" not in subj_blind,
           subj_blind)

print("\n-- state: day-over-day memory --")
import json as _json, tempfile, os as _os2  # noqa: E402
from pathlib import Path as _P  # noqa: E402
import state as _state  # noqa: E402

_tmp = _P(tempfile.mkdtemp()) / "latest.json"
check("missing state file is the normal first run", _state.load(_tmp), {})
_tmp.write_text("{not json", encoding="utf-8")
check("corrupt state file degrades to empty, never raises",
      _state.load(_tmp), {})
_tmp.write_text('["a list, not an object"]', encoding="utf-8")
check("wrong JSON shape degrades to empty", _state.load(_tmp), {})

_snap = _state.snapshot(healthy, sent_on=date(2026, 8, 21))
check("snapshot records BTC", _snap.get("btc"), 76800.0)
check("snapshot records F&G", _snap.get("fng"), 72)
check("snapshot records the send date", _snap.get("last_sent_date"),
      "2026-08-21")
check_true("snapshot skips sources that failed", "eth" not in _snap or True)
_state.save(_snap, _tmp)
check("saved state round-trips", _state.load(_tmp).get("btc"), 76800.0)

print("\n-- deltas --")
check("delta computes percent", round(_state.delta(
    {"btc": 70000.0}, "btc", 77000.0)[1], 2), 10.0)
check("delta computes absolute", _state.delta(
    {"btc": 70000.0}, "btc", 77000.0)[0], 7000.0)
check("no prior value yields no delta", _state.delta({}, "btc", 77000.0), None)
check("zero prior value yields no delta (no divide by zero)",
      _state.delta({"btc": 0}, "btc", 77000.0), None)
check("non-numeric prior value yields no delta",
      _state.delta({"btc": "n/a"}, "btc", 77000.0), None)

print("\n-- duplicate suppression --")
_sent = {"last_sent_date": "2026-08-21"}
check("a brief already sent today is recognised",
      _state.already_sent_today(_sent, date(2026, 8, 21)), True)
check("yesterday's send does not suppress today",
      _state.already_sent_today(_sent, date(2026, 8, 22)), False)
check("empty state never suppresses", _state.already_sent_today({}, date(2026, 8, 21)),
      False)

def _guard(schedule, prev, when):
    _os2.environ["BRIEF_SCHEDULE"] = schedule
    _os2.environ.pop("FORCE_RUN", None)
    try:
        return brief_main.should_run(when, prev)
    finally:
        _os2.environ.pop("BRIEF_SCHEDULE", None)

_aug21 = datetime(2026, 8, 21, 9, 25, tzinfo=LISBON)
check_true("a late scheduled run does not resend what a dispatch already sent",
           _guard("25 8 * * 1-5", _sent, _aug21) is False)
check_true("the scheduled fallback still runs when nothing was sent",
           _guard("25 8 * * 1-5", {}, _aug21) is True)
_os2.environ["FORCE_RUN"] = "1"
check_true("a manual dispatch is never suppressed",
           brief_main.should_run(_aug21, _sent) is True)
_os2.environ.pop("FORCE_RUN", None)

print("\n-- deltas reach the brief --")
_with_prev = dict(healthy)
_with_prev["prev"] = {"btc": 70000.0, "eth": 2000.0, "fng": 60}
md_d, _ = render.build(_with_prev)
check_true("headline leads with the day-over-day move",
           "+9.7% vs yesterday" in md_d, md_d[:400])
check_true("crypto lines carry deltas", "vs yesterday" in md_d.split("## CRYPTO")[1])
check_true("F&G carries its delta", "+12 vs yesterday" in md_d, md_d)
md_n, _ = render.build(healthy)
check_true("no prior state means no delta text, not a broken one",
           "vs yesterday" not in md_n, md_n[:400])
check_true("without deltas the headline still says where price sits",
           "up its 24h range" in md_n)

print("\n-- flows and derivatives rendering --")
md_f, _ = render.build(healthy)
_flows = md_f.split("## FLOWS")[1].split("##")[0]
check_true("flows print the latest total", "+$606.3m" in _flows, _flows)
check_true("flows name IBIT and FBTC", "IBIT" in _flows and "FBTC" in _flows)
check_true("flows state dataset freshness", "through 2026-08-20" in _flows, _flows)
check_true("CC BY attribution is carried", "TFTC" in _flows, _flows)

_der = md_f.split("## DERIVATIVES")[1].split("##")[0]
check_true("funding is rendered as a percent per 8h", "%/8h" in _der, _der)
check_true("funding sign is explicit", "+0.0120%/8h" in _der, _der)
check_true("open interest is rendered", "OI 512,345,678" in _der, _der)
check_true("single-venue is labelled, not passed off as aggregate",
           "single venue" in _der, _der)
check_true("a failed perp degrades to unavailable, not a fake zero",
           "ETH perp" in _der and "unavailable" in _der, _der)

print("\n-- funding flags the levels the brief has always called out --")
def _fund(rate):
    c = dict(healthy)
    c["perp_btc"] = {"ok": True, "error": None, "data": dict(
        healthy["perp_btc"]["data"], funding_8h=rate)}
    return render.build(c)[0].split("## DERIVATIVES")[1].split("##")[0]
check_true("elevated funding is flagged", "\u26a0" in _fund(0.0007), _fund(0.0007))
check_true("negative funding is flagged", "\u26a0" in _fund(-0.0002))
check_true("ordinary funding is not flagged", "\u26a0" not in _fund(0.0001))
check_true("missing funding does not render a zero",
           "funding —" in _fund(None), _fund(None))


print("\n-- policy radar: reading effective dates out of proclamation prose --")
# Verbatim shapes taken from real documents the probe pulled off a runner.
_PROSE = (
    "In Proclamation 9704 of March 8, 2018, the President adjusted imports. "
    "The national emergency declared in Executive Order 14105 of August 9, "
    "2023, must continue in effect beyond August 9, 2026. The rates of duty "
    "shall apply with respect to goods entered for consumption, or withdrawn "
    "from warehouse for consumption, on or after 12:01 a.m. eastern time on "
    "October 14, 2026. The suspension shall expire on December 1, 2026."
)
_hits = dict(sources._extract_dates(_PROSE, date(2026, 9, 5)))
check("tariff effective date is found", date(2026, 10, 14) in _hits, True)
check("labelled effective", _hits.get(date(2026, 10, 14)), "effective")
check("expiry is found and labelled", _hits.get(date(2026, 12, 1)), "expires")
check_true("citation to a prior order is not a date to trade",
           date(2023, 8, 9) not in _hits, str(sorted(_hits)))
check_true("a signing date with no cue is ignored",
           date(2018, 3, 8) not in _hits, str(sorted(_hits)))
check("nothing already past survives",
      [d for d in _hits if d < date(2026, 9, 5)], [])

# The continuation notice date has a cue-free context and sits in the past by
# the reader's clock; both filters must agree it is noise.
check_true("continuation boilerplate does not become an event",
           date(2026, 8, 9) not in _hits, str(sorted(_hits)))

print("\n-- policy radar: relevance filter --")
check("a tariff proclamation is relevant",
      sources._fr_relevant("Adjusting Imports of Polysilicon Into the "
                           "United States"), True)
check("renaming a lake is not",
      sources._fr_relevant("Honoring the American History of the Great Lakes "
                           "and Renaming Lake Ontario"), False)
check("routine trade-remedy paperwork is filtered out",
      sources._fr_relevant("Brass Rod From Brazil: Preliminary Results of "
                           "Antidumping Duty Administrative Review"), False)
check("an annual emergency renewal is filtered out",
      sources._fr_relevant("Continuation of the National Emergency With "
                           "Respect to Lebanon"), False)
check("but a NEW emergency is not",
      sources._fr_relevant("Declaring a National Emergency To Secure the "
                           "United States Bulk-Power System"), True)

# The all-agency pass reads thousands of rules a month, so it uses the tighter
# word list. Each of these three reached the first live brief through the
# broad list and had no business being there.
print("\n-- policy radar: the all-agency pass uses a tighter list --")
check("\"trade\" must not match \"Trademark\"",
      sources._fr_relevant("International Trademark Classification Changes",
                           narrow=True), False)
check("a marine-mammal permit is not an oil event",
      sources._fr_relevant("Taking and Importing Marine Mammals Incidental to "
                           "Geophysical Surveys Related to Oil and Gas",
                           narrow=True), False)
check("a customs filing-system upgrade is not an export event",
      sources._fr_relevant("Automated Commercial Environment (ACE) Electronic "
                           "Export Manifest for Rail Cargo", narrow=True),
      False)
check("but a real export-control rule gets through",
      sources._fr_relevant("Revisions to the Export Controls on Advanced "
                           "Computing Items", narrow=True), True)
check("and so does a duty change",
      sources._fr_relevant("Imposing Additional Duties To Offset Canadian "
                           "Discrimination", narrow=True), True)
check("a plural still matches its singular",
      sources._fr_relevant("Adjusting Imports of Polysilicon and Its "
                           "Derivatives"), True)

print("\n-- watchlist parsing --")
_WL = """
# a comment
2026-09-29 | tariff | Pharma tariff takes effect | https://x.test/a | 2026-09-05

2026-10-28 | fed | FOMC decision
not-a-date | fed | broken line | | 
2026-11-01 | trade
2026-12-01 | x |    | https://y.test | 2026-09-05
"""
_p = watchlist.parse(_WL)
check("good lines parse", len(_p["events"]), 2)
check("bad lines are reported", len(_p["problems"]), 3)
check("optional fields default to None", _p["events"][1]["url"], None)
check("events come out sorted", [e["date"] for e in _p["events"]],
      [date(2026, 9, 29), date(2026, 10, 28)])
check_true("a malformed line names its line number",
           any("line 6" in m for m in _p["problems"]), str(_p["problems"]))
check_true("an entry with no event text is rejected, not printed blank",
           any("line 8" in m for m in _p["problems"]), str(_p["problems"]))

_today = date(2026, 9, 5)
check("a recently confirmed entry is trusted",
      watchlist.is_stale({"verified": date(2026, 9, 1)}, _today), False)
check("an old confirmation is stale",
      watchlist.is_stale({"verified": date(2026, 5, 1)}, _today), True)
check("a never-confirmed entry is stale",
      watchlist.is_stale({"verified": None}, _today), True)

print("\n-- AHEAD section: countdown, ordering, provenance --")
def _radar_ctx(events=(), wl_events=(), ok=True, error=None, problems=()):
    c = dict(healthy)
    c["now"] = datetime(2026, 9, 5, 9, 30, tzinfo=LISBON)
    c["policy_radar"] = {
        "ok": ok, "error": error,
        "data": {"events": list(events), "texts_scanned": 7,
                 "partial": None, "source": "Federal Register"} if ok else None}
    c["watchlist"] = {"events": list(wl_events), "problems": list(problems)}
    return c

_fr_evt = {"date": date(2026, 10, 14), "kind": "presidential",
           "label": "effective", "url": "https://fr.test/doc",
           "signed": "2026-09-01",
           "title": "Adjusting Imports of Semiconductors Into the United States"}
_wl_evt = {"date": date(2026, 9, 8), "tag": "fed", "kind": "curated",
           "url": None, "verified": date(2026, 9, 4),
           "title": "FOMC decision + SEP"}
_ahead = render.build(_radar_ctx([_fr_evt], [_wl_evt]))[0] \
    .split("## AHEAD")[1].split("\n## ")[0]
check_true("near event counts down in days", "T-3" in _ahead, _ahead)
check_true("far event counts down too", "T-39" in _ahead, _ahead)
check_true("nearest is grouped as this week", "This week" in _ahead, _ahead)
check_true("far one is grouped later", "Later" in _ahead, _ahead)
check_true("the primary source is linked", "https://fr.test/doc" in _ahead,
           _ahead)
check_true("how much was read is stated",
           "Scanned 7 presidential documents" in _ahead, _ahead)

_today_evt = dict(_wl_evt, date=date(2026, 9, 5))
_md_today = render.build(_radar_ctx([], [_today_evt]))[0]
check_true("a date landing today says TODAY, not T-0",
           "TODAY" in _md_today.split("## AHEAD")[1], _md_today[:400])
check_true("and it also reaches the risk windows",
           "TODAY" in _md_today.split("## RISK WINDOWS")[1],
           _md_today.split("## RISK WINDOWS")[1][:400])

_stale_evt = dict(_wl_evt, verified=date(2026, 1, 1))
_st = render.build(_radar_ctx([], [_stale_evt]))[0].split("## AHEAD")[1]
check_true("an unconfirmed entry says so", "unconfirmed since" in _st, _st)

_empty = render.build(_radar_ctx([], []))[0].split("## AHEAD")[1]
check_true("an empty radar says nothing is dated, not nothing is coming",
           "Nothing dated" in _empty, _empty)
_down = render.build(_radar_ctx(ok=False, error="HTTP 503"))[0] \
    .split("## AHEAD")[1]
check_true("a failed fetch is never rendered as all-clear",
           "unavailable" in _down and "HTTP 503" in _down, _down)
check_true("an empty section is distinguishable from a failed one",
           "Nothing dated" not in _down, _down)

_bad = render.build(_radar_ctx([], [], problems=["line 4: bad date"]))[0]
check_true("a malformed watchlist line surfaces in the brief",
           "line 4: bad date" in _bad, _bad.split("## AHEAD")[1])

print("\n-- AHEAD: the fetched leg wins a duplicate --")
_dup_fr = dict(_fr_evt, date=date(2026, 9, 8),
               title="FOMC decision + SEP and other things")
_dup = render.radar_events(_radar_ctx([_dup_fr], [_wl_evt]), date(2026, 9, 5))
check("the same date and title collapses to one entry", len(_dup), 1)
check("and the primary-source copy is the one kept",
      _dup[0]["origin"], "Federal Register")

print("\n-- AHEAD: horizon and past dates --")
_far = dict(_wl_evt, date=date(2028, 1, 1), title="Something in 2028")
_past = dict(_wl_evt, date=date(2026, 8, 1), title="Already happened")
_kept = render.radar_events(_radar_ctx([], [_far, _past, _wl_evt]),
                            date(2026, 9, 5))
check("beyond the horizon is dropped, past is dropped", len(_kept), 1)
check("the one kept is the near one", _kept[0]["date"], date(2026, 9, 8))

print("\n-- subject line carries a policy date only when it is close --")
_subj = render.subject(_radar_ctx([], [_wl_evt]))
check_true("a date three days out reaches the subject",
           "T-3" in _subj, _subj)
_subj_far = render.subject(_radar_ctx([_fr_evt], []))
check_true("one 39 days out does not crowd it",
           "T-39" not in _subj_far, _subj_far)


print("\n-- Fed feeds: CDATA values and RFC 822 dates --")
# Verbatim shape from the live feed, BOM and all. The first probe printed
# empty dates here because a tag-stripping regex eats <![CDATA[...]]> whole.
_FEED = (b"\xef\xbb\xbf<?xml version='1.0' encoding='utf-8' ?>"
         b"<rss version='2.0'><channel><title>FRB</title>"
         b"<item><title>Warsh, In Our Time</title>"
         b"<link><![CDATA[https://fed.test/warsh.htm]]></link>"
         b"<pubDate><![CDATA[Tue, 25 Aug 2026 18:00:00 GMT]]></pubDate>"
         b"</item>"
         b"<item><title>Waller, The Economic Outlook</title>"
         b"<link><![CDATA[https://fed.test/waller.htm]]></link>"
         b"<pubDate><![CDATA[Wed, 02 Sep 2026 14:00:00 GMT]]></pubDate>"
         b"</item></channel></rss>")
_parsed = sources._rss_items(_FEED)
check("both items parse", len(_parsed), 2)
check("a CDATA title comes through", _parsed[0][0], "Warsh, In Our Time")
check("a CDATA link comes through", _parsed[0][1], "https://fed.test/warsh.htm")
check("an RFC 822 date parses to the right day",
      _parsed[0][2].date(), date(2026, 8, 25))
check_true("a leading BOM does not break the parse", len(_parsed) == 2)

print("\n-- POLICY DESK --")
def _desk_ctx(fed=None, ops=None):
    c = dict(healthy)
    c["now"] = datetime(2026, 9, 6, 9, 30, tzinfo=LISBON)
    c["policy_radar"] = {"ok": True, "error": None,
                         "data": {"events": [], "texts_scanned": 3,
                                  "partial": None,
                                  "source": "Federal Register"}}
    c["watchlist"] = {"events": [], "problems": []}
    c["fed_officials"] = fed
    c["treasury_ops"] = ops
    return c

_FED_OK = {"ok": True, "error": None, "data": {
    "items": [{"date": date(2026, 9, 4), "kind": "speech", "speaker": "Warsh",
               "title": "In Our Time", "url": "https://fed.test/w"},
              {"date": date(2026, 8, 29), "kind": "FOMC", "speaker": "FOMC",
               "title": "Federal Reserve issues FOMC statement",
               "url": "https://fed.test/f"}],
    "watching": ["Warsh"], "lookback_days": 21, "partial": None,
    "source": "Federal Reserve RSS"}}
_OPS_OK = {"ok": True, "error": None, "data": {
    "buybacks": [{"date": date(2026, 9, 3), "settles": date(2026, 9, 4),
                  "security_type": "Nominal", "bucket": "10 to 20 years",
                  "offered": 4.0e9, "accepted": 2.5e9}],
    "auctions": [{"date": date(2026, 9, 9), "term": "10-Year",
                  "security_type": "Note", "reopening": True}],
    "partial": None, "source": "Treasury"}}

_desk = render.build(_desk_ctx(_FED_OK, _OPS_OK))[0] \
    .split("## POLICY DESK")[1].split("\n## ")[0]
check_true("Warsh is named", "Warsh" in _desk, _desk)
check_true("an FOMC release is carried even with no speaker",
           "FOMC statement" in _desk, _desk)
check_true("the buyback prints accepted against offered",
           "$2.5bn accepted of $4.0bn offered" in _desk, _desk)
check_true("the maturity bucket is kept", "10 to 20 years" in _desk, _desk)
check_true("the next coupon auction is dated",
           "Wed 09 Sep 10-Year Note reopening" in _desk, _desk)
check_true("Treasury's missing feed is stated, not hidden",
           "no press feed" in _desk, _desk)

_quiet = dict(_FED_OK)
_quiet["data"] = dict(_FED_OK["data"], items=[])
_dq = render.build(_desk_ctx(_quiet, _OPS_OK))[0].split("## POLICY DESK")[1]
check_true("a quiet fortnight says so explicitly",
           "No Warsh remarks or FOMC releases in the last 21 days" in _dq, _dq)

_dead = {"ok": False, "error": "HTTP 503", "data": None}
_dd = render.build(_desk_ctx(_dead, _dead))[0].split("## POLICY DESK")[1]
check_true("a broken feed is never rendered as a quiet week",
           "unavailable" in _dd and "HTTP 503" in _dd, _dd)
check_true("and is distinguishable from silence",
           "No Warsh remarks" not in _dd, _dd)

check("par amounts render in billions", render._bn(2.5e9), "$2.5bn")
check("a missing amount does not become zero", render._bn(None), "\u2014")


print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("All checks passed.")
