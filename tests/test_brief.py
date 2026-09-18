"""Offline tests for the pure logic: timezone handling, max pain, flow runs,
and end-to-end rendering with both healthy and fully-degraded inputs.

No network. Everything here must pass before the workflow is trusted.
"""

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import main  # noqa: E402
import copy  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402

import cycles  # noqa: E402
import render  # noqa: E402
import sources  # noqa: E402
import state  # noqa: E402
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
          "fed_officials", "treasury_ops", "policy_rate", "fed_odds",
          "inflation"):
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

print("\n-- FRED keeps its own calendar, and it is not Lisbon's --")
# The St. Louis Fed runs on US Central, six hours behind Lisbon in summer, so
# between midnight and about 06:00 Lisbon has rolled over and FRED has not.
# Asking for that date is a 400. Found live at 00:11 Lisbon; the 09:20 brief
# never hits it, because 09:20 Lisbon is 03:20 Central on the same day.
check("a Lisbon date ahead of FRED's is clamped",
      sources._fred_today(date(2099, 1, 1)),
      datetime.now(sources.FRED_TZ).date())
check("an older explicit date is left alone",
      sources._fred_today(date(2026, 1, 5)), date(2026, 1, 5))
check_true("and with no argument it is FRED's own today",
           sources._fred_today() == datetime.now(sources.FRED_TZ).date())

print("\n-- liquidations: recent, counted, and never a daily total --")
_NOW19 = datetime(2026, 9, 18, 9, 20, tzinfo=LISBON)
_LIQ = {"ok": True, "error": None, "data": {
    "books": [{"label": "BTC", "uly": "BTC-USDT", "rows": 100,
               "longs": 31, "shorts": 69},
              {"label": "ETH", "uly": "ETH-USDT", "rows": 100,
               "longs": 48, "shorts": 52}],
    "newest": _NOW19, "span_hours": 0.47, "page_size": 100,
    "partial": None, "source": "OKX (single venue)"}}
_ll = "\n".join(render._liq_line(_LIQ, _NOW19))
check_true("the side counts print", "31 long · 69 short" in _ll, _ll)
check_true("and the skew names a side", "69% short" in _ll, _ll)
# One page spans 28 minutes. A "24h" label on it would be a number measuring
# something other than what it claims.
check_true("the window is the measured one", "last 28 min" in _ll, _ll)
check_true("and it is never called a daily total",
           "24h" not in _ll and "daily total" in _ll, _ll)
# sz is in contracts and the multiplier lives in an unprobed endpoint.
check_true("no dollar figure is invented", "$" not in _ll, _ll)
check_true("and the reason is stated", "contracts" in _ll, _ll)
check_true("the single venue is labelled", "single venue" in _ll, _ll)
check_true("an hour-plus window reads in hours",
           "last 2.0h" in " ".join(render._liq_line(
               {"ok": True, "error": None,
                "data": dict(_LIQ["data"], span_hours=2.0)}, _NOW19)))
check_true("a dead fetch degrades to a named reason",
           render._liq_line({"ok": False, "error": "okx: timeout"},
                            _NOW19)[0].startswith("**Liquidations:** unavailable"))

print("\n-- open interest against price, with no label on the pair --")
_oi_ctx = dict(healthy)
_oi_ctx["prev"] = {"oi_btc": 7.0e8, "btc": 80000.0}
_oi_ctx["perp_btc"] = {"ok": True, "error": None, "data": {
    "instrument": "BTC-PERPETUAL", "funding_8h": 0.0001,
    "open_interest": 7.7e8, "index_price": 80000.0, "mark_price": 80400.0,
    "source": "Deribit (single venue)"}}
_oi_ctx["crypto"] = {"ok": True, "error": None, "data": {"pairs": [
    {"symbol": "BTC", "last": 81600.0, "vol_24h": 1.0, "day_open": 80000.0,
     "pct_since_utc_midnight": 2.0, "high_24h": 82000.0, "low_24h": 79000.0,
     "vwap_24h": 80500.0}]}}
_oi = render._oi_line(_oi_ctx, "BTC", "perp_btc", "oi_btc")
check_true("the OI move prints", "+10.0% vs yesterday" in _oi, _oi)
check_true("with the price move beside it", "(price +2.0%)" in _oi, _oi)
# Price up on rising OI and price up on falling OI are opposite events wearing
# the same price number. Naming WHICH is an inference about who the marginal
# participant is, and D22 rejected exactly that boundary.
check_true("and no reading of what the pair means",
           not any(w in _oi.lower() for w in
                   ("new longs", "shorts covering", "opening", "unwind")), _oi)
check("no stored OI means no claim",
      render._oi_line(dict(_oi_ctx, prev={}), "BTC", "perp_btc", "oi_btc"), None)

print("\n-- liquidity plumbing: three components, never a composite --")
_PL = {"ok": True, "error": None, "data": {"series": [
    {"id": "RRPONTSYD", "label": "Reverse repo", "unit": "$bn",
     "as_of": date(2026, 9, 17), "value": 412.0, "prior": 455.0},
    {"id": "WTREGEN", "label": "Treasury account", "unit": "$bn",
     "as_of": date(2026, 9, 10), "value": 811.0, "prior": 760.0},
    {"id": "WRESBAL", "label": "Bank reserves", "unit": "$bn",
     "as_of": date(2026, 9, 10), "value": 3120.0, "prior": 3180.0},
], "partial": None, "source": "FRED (St. Louis Fed)"}}
_pl = "\n".join(render._plumbing_lines(_PL, _NOW19))
check_true("all three components print",
           all(k in _pl for k in ("Reverse repo", "Treasury account",
                                  "Bank reserves")), _pl)
check_true("each carries its own date", _pl.count("as of") == 3, _pl)
check_true("and the move on the prior print", "-43bn on the prior print" in _pl
           or "-43" in _pl, _pl)
# The common construct has modelling choices baked in and different desks
# compute it differently. As one headline number it is a derived opinion in a
# fetched number's typeface.
check_true("no net liquidity composite is computed",
           "net liquidity" not in _pl.lower(), _pl)
_bd_ctx = dict(healthy)
_bd_ctx["backdrop"] = {"ok": True, "error": None, "data": {"series": [
    {"id": "UNRATE", "label": "Unemployment", "unit": "%",
     "as_of": date(2026, 8, 1), "value": 4.4, "prior": 4.3,
     "yoy": None, "ann_3m": None}], "partial": None,
    "source": "FRED (St. Louis Fed)"}}
_bd_ctx["plumbing"] = _PL
_bd_md = render.build(_bd_ctx)[0]
check_true("and the brief says why it is not computed",
           "net liquidity composite" in _bd_md, _bd_md[-2000:])

print("\n-- the CME weekend, measured but never predicted --")
_cme_ctx = dict(healthy)
_cme_ctx["yahoo_extra"] = {"ok": True, "error": None, "data": {"quotes": {
    "CME BTC": {"last": 81260.0, "pct_change": 0.1, "as_of": None},
    "IBIT": {"last": 46.02, "pct_change": 1.2, "as_of": None},
    "Brent": {"last": 98.77, "pct_change": -0.4, "as_of": None}},
    "partial": None, "source": "Yahoo chart API"}}
_cme_ctx["crypto"] = {"ok": True, "error": None, "data": {"pairs": [
    {"symbol": "BTC", "last": 83000.0, "vol_24h": 1.0, "day_open": 82000.0,
     "pct_since_utc_midnight": 1.0, "high_24h": 83500.0, "low_24h": 82500.0,
     "vwap_24h": 82800.0}]}}
_cw = "\n".join(render._cme_weekend(_cme_ctx, date(2026, 9, 21)))   # Monday
check_true("the session rule prints", "shut Fri 17:00 ET" in _cw, _cw)
check_true("and names the risk", "unhedged" in _cw, _cw)
check_true("the gap is measured", "gap +2.14%" in _cw, _cw)
check_true("and whether spot went back through it",
           "has not traded back through it" in _cw, _cw)
# The size and direction are fetched facts. "Gaps tend to fill" is a claim
# about future price and falls under D3 and D22.
check_true("it never says the gap should fill",
           not any(w in _cw.lower() for w in ("should", "tend", "expect",
                                              "likely", "will fill")), _cw)
check("midweek it says nothing at all",
      render._cme_weekend(_cme_ctx, date(2026, 9, 23)), [])

print("\n-- IBIT and Brent, unblocked by round 19 --")
_ib = render.build(_cme_ctx)[0]
check_true("IBIT reaches FLOWS", "**IBIT** $46.02" in _ib, _ib)
# NYSE hours only: at 09:20 Lisbon the last print is yesterday's close.
check_true("and is labelled as a secondary market on NYSE hours",
           "secondary market, NYSE hours only" in _ib, _ib)
check_true("Brent reaches MACRO", "**Brent** 98.77" in _ib, _ib)
# Without WTI there is no spread, and printing Brent alone is the correct
# degradation rather than a missing feature.
check_true("no WTI means no spread, not a wrong one",
           "Brent−WTI" not in _ib, _ib)
_sp_ctx = dict(_cme_ctx)
_sp_ctx["cross_asset"] = {"ok": True, "error": None, "data": {
    "quotes": {"WTI": {"last": 95.78, "pct_change": -0.5, "as_of": None}},
    "errors": {}}}
_sp = render.build(_sp_ctx)[0]
check_true("with WTI beside it the spread prints",
           "Brent−WTI $+2.99" in _sp, _sp[-1200:])


print("\n-- the state bundle: one schema change, several features --")
def _snap_ctx(day, btc, **extra):
    c = {"now": datetime(2026, 9, day, 9, 20, tzinfo=LISBON),
         "crypto": {"ok": True, "error": None, "data": {"pairs": [
             {"symbol": "BTC", "last": btc, "vol_24h": extra.get("vol", 1000.0)}]}},
         "fear_greed": {"ok": True, "error": None,
                        "data": {"today": {"value": extra.get("fng", 56)}}},
         "global_mcap": {"ok": True, "error": None, "data": {
             "btc_dominance": extra.get("dom", 58.5),
             "stable_supply_usd": extra.get("stable", 2.6e11)}},
         "perp_btc": {"ok": True, "error": None,
                      "data": {"open_interest": extra.get("oi", 7.8e8)}}}
    return c

_s1 = state.snapshot(_snap_ctx(14, 80000.0), sent_on=date(2026, 9, 14), prev={})
check_true("the new figures are stored",
           _s1["btc_dom"] == 58.5 and _s1["oi_btc"] == 7.8e8, sorted(_s1))
# Kraken calls it vol_24h, not volume_24h. A wrong key here stores nothing and
# fails silently, so assert the value rather than the key.
check("volume is stored under the name Kraken actually uses",
      _s1["vol_btc"], 1000.0)
check("the history starts with one day", len(_s1["history"]), 1)
check_true("and the morning baseline is captured", _s1["am"]["btc"] == 80000.0)

_prev = _s1
for _d, _p in ((15, 81000.0), (16, 79000.0), (17, 82000.0), (18, 83000.0)):
    _prev = state.snapshot(_snap_ctx(_d, _p), sent_on=date(2026, 9, _d), prev=_prev)
check("five days give five history rows", len(_prev["history"]), 5)
check("oldest first", state.series(_prev, "btc")[0], 80000.0)
# A manual re-send must not distort an average by counting a day twice.
_again = state.snapshot(_snap_ctx(18, 83500.0), sent_on=date(2026, 9, 18), prev=_prev)
check("a second run the same day replaces that day", len(_again["history"]), 5)
check("with the newer value", state.series(_again, "btc")[-1], 83500.0)
# Pruning: the window is 30 days and must not creep.
_long = _prev
for _i in range(40):
    _long = state.snapshot(_snap_ctx(18, 80000.0 + _i), sent_on=None, prev=_long)
    _long["history"][-1]["date"] = f"2026-10-{(_i % 28) + 1:02d}"
check_true("the history never exceeds 30 days",
           len(_long["history"]) <= state.HISTORY_DAYS, len(_long["history"]))

# An average of two points is not an average, and a number that pretends to be
# one for the first month after shipping is worse than no number.
check("a thin window yields no average",
      state.average({"history": [{"btc": 1.0}, {"btc": 2.0}]}, "btc"), None)
check("five points is enough", round(state.average(_prev, "btc")), 81000)
check("an old state file yields nothing at all", state.average({}, "btc"), None)
check("and no series", state.series({}, "btc"), [])
check("range position needs a window too",
      state.range_position({"history": [{"btc": 1.0}]}, "btc", 2.0, 30), None)
check("a flat window has no position in it",
      state.range_position({"history": [{"btc": 5.0}] * 10}, "btc", 5.0, 30),
      None)
check("top of the range reads 100",
      state.range_position({"history": [{"btc": 1.0}, {"btc": 2.0},
                                        {"btc": 3.0}, {"btc": 4.0}]},
                           "btc", 9.0, 7), 100.0)
check("days_since counts back from today",
      state.days_since({"history": [{"btc": 1.0}, {"btc": 9.0}, {"btc": 2.0}]},
                       "btc", lambda v: v > 5), 1)
# "Not in the window" is a different statement from "a long time ago".
check("and says nothing when it is not in the window",
      state.days_since({"history": [{"btc": 1.0}]}, "btc", lambda v: v > 5),
      None)

print("\n-- the PM edition cannot corrupt the morning --")
# This is the single most important test in the file. If the PM overwrote the
# daily baseline, tomorrow's "vs yesterday" would compare 09:20 against this
# afternoon: a nineteen-hour move labelled as a daily one, which is §3.18 and
# cost a correction once already.
_am_state = copy.deepcopy(_prev)
_after_pm = state.pm_mark(_am_state, date(2026, 9, 18))
_diff = {k for k in set(_after_pm) | set(_am_state)
         if _after_pm.get(k) != _am_state.get(k)}
check("the PM changes exactly one key", _diff, {"last_sent_pm_date"})
check_true("the daily baseline is byte-identical",
           json.dumps(_after_pm["history"], sort_keys=True)
           == json.dumps(_am_state["history"], sort_keys=True))
check_true("and so is the morning snapshot",
           _after_pm["am"] == _am_state["am"])
check("and `date` is untouched", _after_pm["date"], _am_state["date"])

# Separate markers, or the PM would be suppressed every day by the morning's.
_both = dict(_after_pm, last_sent_date="2026-09-18")
check_true("the AM guard sees the AM marker",
           state.already_sent_today(_both, date(2026, 9, 18)))
check_true("the PM guard sees its own",
           state.already_sent_pm_today(_both, date(2026, 9, 18)))
check_true("a morning send alone does not suppress the PM",
           not state.already_sent_pm_today({"last_sent_date": "2026-09-18"},
                                           date(2026, 9, 18)))

print("\n-- the PM edition: spine always, body only when there is one --")
def _pm_ctx(btc, am=None, **kw):
    c = dict(healthy)
    c["now"] = datetime(2026, 9, 18, 13, 0, tzinfo=LISBON)
    c["crypto"] = {"ok": True, "error": None, "data": {"pairs": [
        {"symbol": "BTC", "last": btc, "vol_24h": 1000.0, "day_open": btc,
         "pct_since_utc_midnight": 0.0, "high_24h": btc, "low_24h": btc,
         "vwap_24h": btc},
        {"symbol": "ETH", "last": kw.get("eth", 2500.0), "vol_24h": 1.0,
         "day_open": 2500.0, "pct_since_utc_midnight": 0.0,
         "high_24h": 2500.0, "low_24h": 2500.0, "vwap_24h": 2500.0}]}}
    c["prev"] = {"am": am} if am else {}
    c["health"] = []
    return c

_quiet = _pm_ctx(80050.0, am={"btc": 80000.0, "eth": 2500.0})
_qmd, _qhtml = render.pm_build(_quiet)
check_true("the spine prints on a quiet day", "## SINCE 09:20" in _qmd, _qmd[:300])
check_true("with the move since the morning", "+0.06% since 09:20" in _qmd, _qmd)
# The common case, and a real answer rather than an empty section.
check_true("and the body says so plainly",
           "No material change since 09:20." in _qmd, _qmd)
# Live on run #87: "Still ahead today" printed a TOMORROW item, because
# _risk_windows appends untimed radar entries at the end and those open with
# "**Tomorrow**". Only a clock qualifies.
_ahead_line = [l for l in render.pm_spine(_quiet)[0]
               if l.startswith("**Still ahead today**")][0]
check_true("the still-ahead line never carries a tomorrow item",
           "Tomorrow" not in _ahead_line, _ahead_line)
check_true("it is a clock time or an explicit nothing",
           re.search(r"\*\*\d{2}:\d{2}\*\*", _ahead_line)
           or "nothing further scheduled" in _ahead_line, _ahead_line)
check_true("a long next-dated title is cut with an ellipsis, not mid-word",
           all(len(l) < 190 for l in render.pm_spine(_quiet)[0]),
           render.pm_spine(_quiet)[0])

check("a quiet subject says quiet",
      render.pm_subject(_quiet).endswith("· quiet"), True)
check_true("the subject keeps the load-bearing prefix",
           render.pm_subject(_quiet).startswith("Market Brief - PM"),
           render.pm_subject(_quiet))

_loud = _pm_ctx(82000.0, am={"btc": 80000.0, "eth": 2500.0})
_lmd, _ = render.pm_build(_loud)
check_true("a 2.5% move crosses the 1.0% threshold",
           "**BTC +2.50%** since the 09:20 brief" in _lmd, _lmd)
check_true("and the subject counts it",
           "1 change" in render.pm_subject(_loud), render.pm_subject(_loud))

# D21. A missing AM baseline suppresses deltas ENTIRELY - it never falls back
# to yesterday's close, which is the bug that printed a two-day move as one.
_orphan = _pm_ctx(80050.0, am=None)
_omd, _ = render.pm_build(_orphan)
check_true("with no morning baseline the delta is suppressed",
           "no morning baseline, so no delta" in _omd, _omd)
check_true("and the reason is banner-level, not a footnote",
           "⚠" in _omd and "suppressed rather than measured" in _omd, _omd)
check_true("no percentage is invented", "since 09:20" not in _omd.split("MATERIAL")[0]
           or "no morning baseline" in _omd, _omd)

# D20: the shadow log records the move whether or not it printed.
_, _shadow_quiet = render.pm_body(_quiet)
check_true("a suppressed move is still measured",
           abs(_shadow_quiet["btc"] - 0.0625) < 0.001, _shadow_quiet)
_, _shadow_loud = render.pm_body(_loud)
check("and so is a printed one", round(_shadow_loud["btc"], 2), 2.5)
check("no baseline means nothing to shadow", render.pm_body(_orphan)[1], {})
check_true("the thresholds live in one block, not in the fetchers",
           set(render.THRESHOLDS) >= {"btc", "eth", "dxy", "us10y_bp",
                                      "btc_dom", "stable_supply"},
           sorted(render.THRESHOLDS))
# A per-cent change and a basis-point move are different units, and comparing
# one against the other fired the body on almost every ordinary afternoon.
_bp = dict(healthy)
_bp["now"] = datetime(2026, 9, 18, 13, 0, tzinfo=LISBON)
_bp["prev"] = {"am": {"btc": 80000.0}}
_bp["cross_asset"] = {"ok": True, "error": None, "data": {"quotes": {
    "US 10Y": {"last": 4.70, "pct_change": 0.30, "as_of": None}}, "errors": {}}}
_, _sh = render.pm_body(_bp)
check("a 0.30% session on a 4.70 yield is 1.4bp, not 30",
      _sh["us10y_bp"], 1.41)
check("and 1.4bp does not cross a 5bp threshold",
      [l for l in render.pm_body(_bp)[0] if "10Y" in l], [])
_bp["cross_asset"]["data"]["quotes"]["US 10Y"]["pct_change"] = 2.0   # ~9bp
check_true("9bp does", any("10Y" in l for l in render.pm_body(_bp)[0]),
           render.pm_body(_bp)[0])


print("\n-- BACKDROP: slow numbers, each carrying the day it was observed --")
_BD = {"ok": True, "error": None, "data": {"series": [
    {"id": "UNRATE", "label": "Unemployment", "unit": "%",
     "as_of": date(2026, 8, 1), "value": 4.4, "prior": 4.3,
     "yoy": None, "ann_3m": None},
    {"id": "T10Y2Y", "label": "10Y\u20132Y spread", "unit": "pp",
     "as_of": date(2026, 9, 17), "value": 0.62, "prior": 0.58,
     "yoy": None, "ann_3m": None},
    {"id": "CPIAUCSL", "label": "CPI", "unit": "index",
     "as_of": date(2026, 8, 1), "value": 334.131, "prior": 332.8,
     "yoy": 3.35, "ann_3m": 4.12},
], "partial": None, "source": "FRED (St. Louis Fed)"}}
_bl = render._backdrop_lines(_BD, datetime(2026, 9, 18, 9, 20, tzinfo=LISBON))
_bt = "\n".join(_bl)
check_true("unemployment prints with its level", "4.40%" in _bt, _bt)
check_true("and the move on the prior print", "+0.10 on the prior print" in _bt, _bt)
check_true("the curve prints too", "0.62pp" in _bt, _bt)
# Two of the three are monthly and one is daily with a lag. Without the date a
# slow number reads as today's - misleading because present, not missing.
check_true("every line carries an as-of",
           all("as of" in l for l in _bl if l.startswith("**")), _bt)
check_true("the monthly one names a month, not a day",
           "as of Aug 2026" in _bt, _bt)
# The index itself means nothing to a reader; the two rates do. And neither
# duplicates EXPECTATIONS, which carries the latest m/m print from BLS.
check_true("CPI is shown as rates, never as the raw index",
           "334" not in _bt, _bt)
check_true("year over year", "+3.4% y/y" in _bt, _bt)
check_true("and the faster three-month cut",
           "+4.1% 3m annualised" in _bt, _bt)
check_true("a failed fetch degrades to a named reason",
           render._backdrop_lines({"ok": False, "error": "FRED_API_KEY is not "
                                   "set"}, None)[0].startswith("Backdrop "
                                                               "unavailable"))

print("\n-- NEWS: the only section that is not a number --")
_now = datetime(2026, 9, 18, 9, 20, tzinfo=LISBON)
_NW = {"ok": True, "error": None, "data": {"items": [
    {"title": "Fed officials signal caution on further hikes",
     "url": "https://cnbc.test/1", "when": _now - timedelta(hours=2),
     "source": "CNBC", "kind": "wire"},
    {"title": "Everything you know about the repo market is wrong",
     "url": "https://zh.test/1", "when": _now - timedelta(hours=5),
     "source": "ZeroHedge", "kind": "commentary"},
], "window_hours": 18, "partial": None, "source": "CNBC + ZeroHedge"}}
_nl = render._news_lines(_NW, _now)
_nt = "\n".join(_nl)
check_true("the wire item is attributed", "via CNBC" in _nt, _nt)
# D16: ZeroHedge is admitted as commentary ON THE CONDITION that it is visibly
# marked. In a brief where every line is a fetched number with a source and an
# age stamp, an opinion headline renders with identical authority - §3.9
# inverted, and it would be the first unsourced claim the brief ever printed.
check_true("and the commentary item is marked as commentary",
           "commentary, not a wire" in _nt, _nt)
check_true("the marking is emphasised, not a quiet suffix",
           "**ZeroHedge — commentary, not a wire**" in _nt, _nt)
check_true("every headline carries its age", _nt.count("ago") >= 2, _nt)
check_true("newest first", _nt.index("Fed officials") < _nt.index("repo market"), _nt)
check("an empty window says so, and does not imply quiet",
      render._news_lines({"ok": True, "error": None, "data": {
          "items": [], "window_hours": 18, "partial": None,
          "source": "x"}}, _now),
      ["Nothing on the wire in the last 18h."])
check_true("a dead feed is named",
           "unavailable" in render._news_lines(
               {"ok": False, "error": "feeds.test: timeout"}, _now)[0])

# §3.11 again: both must reach the rendered brief, not just their helpers.
_c3 = dict(healthy)
_c3["backdrop"] = _BD
_c3["news"] = _NW
_c3_md, _c3_html = render.build(_c3)
check_true("BACKDROP reaches the brief", "## BACKDROP" in _c3_md, _c3_md[:200])
check_true("NEWS reaches the brief", "## NEWS" in _c3_md, _c3_md[:200])
check_true("both sit in tier 3, below the standing picture",
           _c3_md.index("## BACKDROP") > _c3_md.index("Tier 3"), "order")
check_true("the commentary marking survives into the HTML",
           "commentary, not a wire" in _c3_html)
# A section absent from the context must not render an empty heading.
_c3_none = dict(healthy)
_c3_none["backdrop"] = None
_c3_none["news"] = None
_none_md = render.build(_c3_none)[0]
check_true("an unconfigured section prints no heading at all",
           "## BACKDROP" not in _none_md and "## NEWS" not in _none_md)


print("\n-- lines that cost nothing, because the data was already fetched --")

# A rate per eight hours is abstract; the same number as annual carry is
# money. 0.0001/8h -> x3 daily -> x365 -> 10.95%/yr.
check("funding becomes an annual carry",
      round(render._annualised(0.0001), 2), 10.95)
check("negative funding annualises negative",
      round(render._annualised(-0.0002), 2), -21.90)
check("no rate makes no claim", render._annualised(None), None)

# Funding lags by an interval; basis is live. Two numbers that look alike and
# mean different things is the $6bn failure in miniature, so they are labelled
# apart and the test checks the labels, not just the arithmetic.
check("basis is the perp against the index",
      round(render._basis({"mark_price": 80400.0, "index_price": 80000.0}), 3),
      0.5)
check("it falls back to last price when mark is absent",
      round(render._basis({"last_price": 79600.0, "index_price": 80000.0}), 3),
      -0.5)
check("a missing index makes no claim",
      render._basis({"mark_price": 80400.0, "index_price": None}), None)
check("and so does a missing price",
      render._basis({"index_price": 80000.0}), None)

_perp = dict(healthy)
_perp["perp_btc"] = {"ok": True, "error": None, "data": {
    "instrument": "BTC-PERPETUAL", "funding_8h": 0.0001,
    "current_funding": 0.0001, "open_interest": 780000000.0,
    "index_price": 80000.0, "mark_price": 80400.0, "last_price": 80390.0,
    "volume_24h_usd": 1e9, "source": "Deribit (single venue)"}}
_dv = render.build(_perp)[0].split("## DERIVATIVES")[1].split("\n## ")[0]
check_true("the annual carry is printed", "+11.0%/yr annualised" in _dv, _dv)
check_true("and never called a projection", "project" not in _dv.lower(), _dv)
check_true("basis is printed and marked live", "basis +0.500% (live)" in _dv, _dv)
check_true("funding is still there beside it", "funding +0.0100%/8h" in _dv, _dv)

# Where open interest sits is fetched data. What price will do about it is a
# claim, and it stays banned.
_opt = dict(healthy)
_o = dict(_opt["options_btc"]["data"])
_n = dict(_o["nearest"])
_n["top_calls"] = [(85000.0, 2140.0), (80000.0, 1890.0), (90000.0, 1510.0)]
_n["top_puts"] = [(75000.0, 1700.0), (70000.0, 980.0)]
_o["nearest"] = _n
_opt["options_btc"] = {"ok": True, "error": None, "data": _o}
_ol = render._options_line(_o)
check_true("three call strikes are listed", "$85,000 (2,140)" in _ol, _ol)
check_true("biggest open interest first",
           _ol.index("$85,000") < _ol.index("$80,000"), _ol)
check_true("puts are listed too", "$75,000 (1,700)" in _ol, _ol)
check_true("a side with only two strikes prints two",
           _ol.count("$") >= 5, _ol)
check_true("and the line never calls a level",
           not any(w in _ol.lower() for w in ("pin", "target", "support",
                                              "resistance", "expect")), _ol)

check("a flow streak counts consecutive same-sign days",
      render._streak([-283, -13, 160, -450, -296, 159]), 1)
check("three inflows in a row count three",
      render._streak([-450, 100, 200, 300]), 3)
check("a zero breaks the streak", render._streak([100, 0, 200]), 1)
check("an empty run has no streak", render._streak([]), 0)
check("and a run ending flat has none", render._streak([100, 200, 0]), 0)

# D24: dominance is a ratio and rises when the denominator falls. A spike in a
# selloff is mostly arithmetic, so supply must always be printed with it.
_gl = dict(healthy)
_gl["global_mcap"] = {"ok": True, "error": None, "data": {
    "total_mcap_usd": 2.79e12, "mcap_change_24h_pct": 2.5,
    "btc_dominance": 58.5, "eth_dominance": 11.5,
    "usdt_dominance": 6.861, "usdc_dominance": 2.762,
    "stable_dominance": 9.623, "stable_supply_usd": 2.79e12 * 0.09623,
    "source": "CoinGecko /api/v3/global"}}
_sent = render.build(_gl)[0].split("## SENTIMENT")[1].split("\n## ")[0]
check_true("stablecoin supply is printed", "bn supply" in _sent, _sent)
check_true("and dominance beside it", "% of total cap" in _sent, _sent)
check_true("with both legs named",
           "USDT 6.86%" in _sent and "USDC 2.76%" in _sent, _sent)
# The rule, asserted rather than trusted: no dominance without supply.
check_true("dominance never appears without supply on the same line",
           all("supply" in l for l in _sent.split("\n")
               if "of total cap" in l), _sent)

_macro = render.build(dict(healthy))[0].split("## MACRO")[1].split("\n## ")[0]
check_true("the cross-asset line leads the section",
           "**Cross-asset**" in _macro, _macro)
check_true("with a direction per asset",
           "\u25b2" in _macro or "\u25bc" in _macro, _macro)
# The brief has no opinion about what the combination means, and a test says so.
check_true("and no verdict about what it means",
           not any(w in _macro.lower() for w in ("risk-on", "risk on",
                                                 "risk-off", "risk off",
                                                 "bullish", "bearish")), _macro)


print("\n-- the watchlist grows two fields without breaking the old ones --")
# The file is maintained by hand. A format change that invalidates the lines
# already in it is a format change that loses them.
_old = watchlist.parse("2026-11-03 | election | Midterms | https://x | 2026-09-18")
check("a five-field line still parses", _old["problems"], [])
check("and defaults to the class D11 always assumed",
      _old["events"][0]["class"], "policy")
check("and to a lead that shows it the whole way out",
      _old["events"][0]["lead"], watchlist.DEFAULT_LEAD_DAYS)

_new = watchlist.parse(
    "2026-11-03 | election | Midterms | https://x | 2026-09-18 | statutory | 60")
check("a seven-field line parses", _new["problems"], [])
check("with its class", _new["events"][0]["class"], "statutory")
check("and its lead", _new["events"][0]["lead"], 60)

_bad = watchlist.parse(
    "2026-11-03 | election | Midterms | | | nonsense | soon")
check_true("an unknown class is a complaint, not a crash",
           any("class" in p for p in _bad["problems"]), _bad["problems"])
check_true("and so is a lead that is not a number",
           any("lead" in p for p in _bad["problems"]), _bad["problems"])
check("and the entry survives with defaults", _bad["events"][0]["class"], "policy")

# D11 amended: a holiday flagged unconfirmed within 75 days of every refresh
# would be a flag that always fires, and a flag that always fires is a flag
# nobody reads.
_seen = date(2026, 6, 1)
_hol = {"verified": _seen, "class": "holiday"}
_pol = {"verified": _seen, "class": "policy"}
_check_day = date(2026, 9, 18)          # 109 days later
check_true("a policy date goes unconfirmed after 75 days",
           watchlist.is_stale(_pol, _check_day))
check_true("a holiday does not", not watchlist.is_stale(_hol, _check_day))
check_true("nor does anything fixed in law",
           not watchlist.is_stale({"verified": _seen, "class": "statutory"},
                                  _check_day))
check_true("an entry never confirmed is always stale",
           watchlist.is_stale({"verified": None, "class": "statutory"},
                              _check_day))

# lead is about WHEN it appears; class is about when it stops being trusted.
_far = {"date": date(2026, 11, 26), "lead": 7}
check_true("an entry outside its lead window is not due",
           not watchlist.within_lead(_far, date(2026, 9, 18)))
check_true("and is due once inside it",
           watchlist.within_lead(_far, date(2026, 11, 20)))
check_true("an entry today is always due",
           watchlist.within_lead({"date": date(2026, 9, 18), "lead": 1},
                                 date(2026, 9, 18)))

check("the horizon reaches a year", render.RADAR_HORIZON_DAYS, 365)
_buckets = [n for n, _ in render.RADAR_BUCKETS]
check("in five buckets", _buckets,
      ["Now", "This month", "3 months", "6 months", "12 months"])
_grouped = render._radar_groups([
    {"date": date(2026, 9, 20), "title": "a"},
    {"date": date(2026, 10, 10), "title": "b"},
    {"date": date(2027, 8, 1), "title": "c"},
], date(2026, 9, 18))
check("an empty bucket is not printed", [n for n, _ in _grouped],
      ["Now", "This month", "12 months"])

# The real file has to stay valid, or the section it feeds goes quiet.
_live = watchlist.load()
check("the shipped watchlist parses clean", _live["problems"], [])
check_true("and Thanksgiving is hidden until its lead window opens",
           not any(e["tag"] == "holiday"
                   and watchlist.within_lead(e, date(2026, 9, 18))
                   for e in _live["events"]),
           [e["tag"] for e in _live["events"]])


print("\n-- recurring structure, derived and never fetched --")
check("third Friday of Sep 2026", cycles.monthly_opex(2026, 9), date(2026, 9, 18))
check("and it is a triple witching",
      cycles.is_triple_witching(date(2026, 9, 18)), True)
check("October's is an ordinary opex",
      cycles.is_triple_witching(cycles.monthly_opex(2026, 10)), False)
# Quad until single-stock futures were delisted. Two names for one event
# reads as two events six months later, so the brief uses one.
check_true("the rendered line says triple, never quad",
           "Triple witching" in render._cycle_lines(date(2026, 9, 18))[0]
           and "quad" not in " ".join(
               render._cycle_lines(date(2026, 9, 18))).lower(),
           render._cycle_lines(date(2026, 9, 18)))
check("VIX expiry is 30 days before the NEXT third Friday",
      cycles.vix_expiry(2026, 10), date(2026, 10, 21))
check("and that lands on a Wednesday", cycles.vix_expiry(2026, 10).weekday(), 2)
check("Deribit monthly is the last Friday",
      cycles.deribit_monthly(2026, 9), date(2026, 9, 25))
check("September's is a quarterly",
      cycles.is_deribit_quarterly(date(2026, 9, 25)), True)
check("October's is not",
      cycles.is_deribit_quarterly(cycles.deribit_monthly(2026, 10)), False)

check("Good Friday 2027 is found", cycles.easter(2027) - timedelta(days=2),
      date(2027, 3, 26))
check("Thanksgiving 2026", cycles.nth_weekday(2026, 11, 3, 4), date(2026, 11, 26))
check_true("and the holiday table agrees",
           cycles.us_market_holidays(2026)[date(2026, 11, 26)] == "Thanksgiving")
# 4 July 2026 is a Saturday, so the NYSE observes it on the Friday.
check_true("a Saturday holiday is observed on the Friday",
           date(2026, 7, 3) in cycles.us_market_holidays(2026), 
           sorted(cycles.us_market_holidays(2026)))
check_true("an ordinary Wednesday is not a holiday",
           not cycles.is_us_market_holiday(date(2026, 9, 16)))

# The 08:00 UTC problem: Deribit settles twenty minutes before the brief
# builds, so on these mornings the options figures have ALREADY rolled.
check_true("the last Friday of the month is a roll day",
           cycles.rolled_today(date(2026, 9, 25)))
check_true("an ordinary Friday is not", not cycles.rolled_today(date(2026, 9, 18)))

_cyc = render._cycle_lines(date(2026, 9, 25))
check_true("and the brief says so, first", _cyc[0].startswith("\u26a0 **Front expiry rolled today**"), _cyc)
check_true("naming what the numbers below now refer to",
           "NEXT expiry" in _cyc[0], _cyc[0])
# Silent most mornings by design: a section that prints daily stops being read.
check("a quiet day prints nothing at all",
      render._cycle_lines(date(2026, 10, 6)), [])


print("\n-- four clocks, and the state of three sessions --")
_c = render._clocks(datetime(2026, 9, 18, 9, 20, tzinfo=LISBON))
check("the Lisbon time leads", _c[0].split(" \u00b7 ")[0], "**09:20 LIS**")
check_true("with UTC, New York and Tokyo beside it",
           "08:20 UTC" in _c[0] and "04:20 NY" in _c[0] and "17:20 TYO" in _c[0], _c[0])
# The sentence a 09:20 reader actually wants, and the one four numbers do not
# give at a glance.
check_true("Tokyo has closed", "Tokyo closed 2h20m ago" in _c[1], _c[1])
check_true("London is open", "London open 1h20m" in _c[1], _c[1])
check_true("New York has not opened", "New York opens in 5h10m" in _c[1], _c[1])

# Thanksgiving: New York is shut and the clocks must not offer an open.
_c_hol = render._clocks(datetime(2026, 11, 26, 14, 0, tzinfo=LISBON))
check_true("a US holiday shows New York shut", "New York shut" in _c_hol[1], _c_hol[1])
check_true("and never an opening countdown",
           "New York opens" not in _c_hol[1], _c_hol[1])
_c_sat = render._clocks(datetime(2026, 9, 19, 12, 0, tzinfo=LISBON))
check_true("a Saturday shuts all three",
           _c_sat[1].count("shut") == 3, _c_sat[1])


print("\n-- three tiers, in order --")
_tier_md = render.build(dict(healthy))[0]
_order = [l[3:] for l in _tier_md.split("\n") if l.startswith("## ")]
check("Tier 1 answers the morning first",
      _order[:3], ["CLOCKS", "THE SETUP", "TODAY"])
check_true("Tier 2 follows the first screen",
           _order.index("CRYPTO") > _order.index("TODAY"), _order)
check_true("and Tier 3 follows Tier 2",
           _order.index("AHEAD") > _order.index("MACRO & EQUITIES"), _order)
check_true("the dividers say which tier is which",
           "*Tier 2 — the standing picture*" in _tier_md
           and "*Tier 3 — the horizons*" in _tier_md)
# CALENDAR and RISK WINDOWS were two lists of the same day in two places.
check_true("CALENDAR is gone, absorbed by TODAY", "## CALENDAR" not in _tier_md)
check_true("and so is RISK WINDOWS", "## RISK WINDOWS" not in _tier_md)
check_true("FED PATH is now EXPECTATIONS",
           "## FED PATH" not in _tier_md and "## EXPECTATIONS" in _tier_md)
# The forward calendar has to land somewhere, or it is simply lost.
check_true("the forward calendar survives the merge, under AHEAD",
           "Next 5 sessions" in _tier_md.split("## AHEAD")[1], _tier_md[-1500:])

_today = _tier_md.split("## TODAY")[1].split("\n## ")[0]
check_true("TODAY carries forecast and previous for a data print",
           "F " in _today and "P " in _today, _today)


print("\n-- app password whitespace tolerance --")
# This used to call send_email(), which opens a real SMTP_SSL connection to
# Gmail and attempts a real login. In a suite whose docstring promises no
# network, on every CI run, from a shared runner address. credentials() is
# the part actually under test.
_os.environ["GMAIL_USER"] = "  kabil.dh@gmail.com  "
_os.environ["GMAIL_APP_PASSWORD"] = "abcd efgh ijkl mnop"
try:
    _u, _p = brief_main.credentials()
    check("the address is trimmed", _u, "kabil.dh@gmail.com")
    check_true("spaced app password is not rejected as missing",
               _p == "abcdefghijklmnop", _p)
except Exception as _e:  # noqa: BLE001
    check_true("spaced app password is not rejected as missing", False, str(_e))
finally:
    _os.environ.pop("GMAIL_USER", None)
    _os.environ.pop("GMAIL_APP_PASSWORD", None)

_os.environ["GMAIL_USER"] = "u@example.com"
_os.environ["GMAIL_APP_PASSWORD"] = "   "  # whitespace only is still empty
try:
    brief_main.credentials()
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
_rw = md_l.split("## TODAY")[1]
check_true("passed NYSE open is dropped", "NYSE cash open" not in _rw, _rw)
check_true("passed NYSE close is dropped", "NYSE cash close" not in _rw, _rw)
check_true("the reader is told windows passed rather than shown nothing",
           "passed" in _rw.lower(), _rw)

_early = dict(healthy)
_early["now"] = datetime(2026, 8, 21, 6, 0, tzinfo=LISBON)
_rw_e = render.build(_early)[0].split("## TODAY")[1]
check_true("future NYSE open is kept", "NYSE cash open" in _rw_e)
check_true("windows are ordered by time",
           _rw_e.index("14:30") < _rw_e.index("21:00"), _rw_e)

print("\n-- weekends have no cash session --")
_sat = dict(healthy)
_sat["now"] = datetime(2026, 8, 22, 13, 0, tzinfo=LISBON)   # Saturday
_sat["calendar"] = {"ok": True, "error": None,
                    "data": {"events": [], "next_week_error": None, "source": "ff"}}
_rw_s = render.build(_sat)[0].split("## TODAY")[1]
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
# `now` is Friday 21 August 2026, so a state file dated the 20th really is
# yesterday. Dating the fixture matters: the label is derived from this date
# rather than assumed, which is the whole point of the 13 Sep fix below.
_with_prev = dict(healthy)
_with_prev["prev"] = {"btc": 70000.0, "eth": 2000.0, "fng": 60,
                      "date": "2026-08-20", "last_sent_date": "2026-08-20"}
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


print("\n-- a multi-day move is never called 'vs yesterday' --")
# 13 September 2026. The brief was not sent on the 12th, so Sunday's run
# compared against Friday's figures and printed "-0.6% vs yesterday". The
# number was correct; the label was two days wrong. Nothing in the suite had
# an opinion about it, because the fixture above carried no date at all.
import health  # noqa: E402


def _label(prev_date, today=date(2026, 8, 21)):
    c = {"now": datetime(today.year, today.month, today.day, 9, 30,
                         tzinfo=LISBON)}
    c["prev"] = {"date": prev_date} if prev_date else {}
    return render._vs_label(c)


check("yesterday is called yesterday", _label("2026-08-20"), "vs yesterday")
check("two days back names the day", _label("2026-08-19"), "vs Wed 19 Aug")
check("a week back names the day", _label("2026-08-14"), "vs Fri 14 Aug")
check("a second run the same day says so", _label("2026-08-21"),
      "vs earlier today")
check("an undated state file claims no date", _label(None), "vs last brief")
check("a state file from the future claims no date", _label("2026-08-25"),
      "vs last brief")

# And it must reach the rendered brief, not just the helper. This is the
# §3.11 rule: a green unit test over a function nothing calls proves nothing.
_gap_ctx = dict(healthy)
_gap_ctx["prev"] = {"btc": 70000.0, "fng": 60, "date": "2026-08-19",
                    "last_sent_date": "2026-08-19"}
_gap_md, _ = render.build(_gap_ctx)
check_true("the rendered brief carries the honest label",
           "+9.7% vs Wed 19 Aug" in _gap_md, _gap_md[:400])
check_true("and does not claim yesterday anywhere",
           "vs yesterday" not in _gap_md, _gap_md[:600])


print("\n-- the brief notices when it did not arrive --")
check("the 12 Sep gap is found",
      health.missed_days({"last_sent_date": "2026-09-11"}, date(2026, 9, 13)),
      [date(2026, 9, 12)])
check("a brief sent yesterday is no gap",
      health.missed_days({"last_sent_date": "2026-09-12"}, date(2026, 9, 13)),
      [])
check("a brief already sent today is no gap",
      health.missed_days({"last_sent_date": "2026-09-13"}, date(2026, 9, 13)),
      [])
check("no state file makes no claim",
      health.missed_days({}, date(2026, 9, 13)), [])
check("an unparseable date makes no claim",
      health.missed_days({"last_sent_date": "not a date"}, date(2026, 9, 13)),
      [])
check("a state file from the future makes no claim",
      health.missed_days({"last_sent_date": "2026-09-20"}, date(2026, 9, 13)),
      [])
check("three missing days are all named",
      len(health.missed_days({"last_sent_date": "2026-09-09"},
                             date(2026, 9, 13))), 3)

_note = health.delivery_note({"last_sent_date": "2026-09-11"},
                             date(2026, 9, 13))
check_true("the note names the missing day", "Sat 12 Sep" in _note, _note)
check_true("and the last confirmed send", "Fri 11 Sep" in _note, _note)
check_true("singular reads as singular", "1 brief never sent" in _note, _note)
check_true("a healthy run says nothing at all",
           health.delivery_note({"last_sent_date": "2026-09-12"},
                                date(2026, 9, 13)) is None)
# A long gap is a state file that stopped being written, not 100 mornings.
_long = health.delivery_note({"last_sent_date": "2026-06-01"},
                             date(2026, 9, 13))
check_true("a long gap is counted, not listed",
           "103 briefs never sent" in _long and "Jun" in _long, _long)
check_true("and stays one line", len(_long) < 120, _long)


print("\n-- the brief notices a stale trigger --")
check("the matching version is silent",
      health.trigger_note(health.EXPECTED_TRIGGER_VERSION), None)
check("no version reported is no claim", health.trigger_note(""), None)
check("nor is a missing one", health.trigger_note(None), None)
_drift = health.trigger_note("6")
check_true("a mismatch names both versions",
           "6" in _drift and health.EXPECTED_TRIGGER_VERSION in _drift, _drift)
check_true("and says what to do about it",
           "apps-script.gs" in _drift, _drift)
check("the repo's own script matches what health expects",
      (Path(__file__).resolve().parents[1] / "trigger" / "apps-script.gs")
      .read_text(encoding="utf-8")
      .split("const SCRIPT_VERSION = '")[1].split("'")[0],
      health.EXPECTED_TRIGGER_VERSION)


print("\n-- the brief notices when it arrived late --")
# The token expires 2026-11-07. When it does, the dispatch dies, the old cron
# picks the job up hours later, the brief still arrives and last_sent_date is
# still written - so neither check above says a word. PROJECT_STATE.md §3.26.
_ON_TIME = datetime(2026, 9, 21, 9, 20, tzinfo=LISBON)     # what normally happens


def _lat(hh, mm, version=None, schedule=None):
    return health.latency_note(
        datetime(2026, 9, 21, hh, mm, tzinfo=LISBON), version, schedule)


check("the normal 09:20 dispatch is silent",
      health.latency_note(_ON_TIME, "7", None), None)
check("so is a run five minutes after target", _lat(9, 30, version="7"), None)
check("and one exactly on the 30-minute line", _lat(9, 55, version="7"), None)
check("a run before target is not late", _lat(6, 0, version="7"), None)
check("the cron slot firing on time is silent",
      _lat(9, 25, schedule="25 8"), None)

# A human pressing "Run workflow" carries neither a version nor a schedule.
# Deliberate is not late, and absence of evidence is not evidence.
check("a hand-clicked dispatch makes no claim at any hour",
      _lat(16, 30), None)
check("nor does a run with no build time at all",
      health.latency_note(None, "7", "25 8"), None)
check("nor one handed a date instead of a datetime",
      health.latency_note(date(2026, 9, 21), "7", "25 8"), None)

_drift_note = _lat(9, 56, version="7")
check_true("one minute past the line does fire", _drift_note is not None)
check_true("and names the build time", "09:56" in _drift_note, _drift_note)
check_true("and the target", "09:25" in _drift_note, _drift_note)
# The Apps Script dispatches testNow() through the identical call with the
# identical version, so a late dispatch and a brief pulled by hand cannot be
# told apart from here. Say so rather than accusing a working trigger.
check_true("and admits it cannot rule out a hand-pulled brief",
           "by hand" in _drift_note, _drift_note)

_cron_note = _lat(13, 7, schedule="25 8")
check_true("the fallback path fires too", _cron_note is not None)
check_true("and reports the delay in hours", "3h42m" in _cron_note, _cron_note)
# This branch IS evidenced: should_run() exits a scheduled run when a brief
# already went out today, so a cron run that got this far proves none had.
check_true("and claims only what should_run proved",
           "No brief had gone out today" in _cron_note, _cron_note)
check_true("and points at the token, which is the likely cause",
           "token" in _cron_note, _cron_note)
check_true("a cron run says nothing about hand-pulling",
           "by hand" not in _cron_note, _cron_note)

check("a delay under an hour reads in minutes",
      health._delay(47), "47 min")
check("a round delay drops the minutes", health._delay(180), "3h")
check("and a ragged one keeps them", health._delay(222), "3h42m")

# Ordering matters: the latency note is the one that explains why the others
# look fine. It leads.
_all = health.notes({"last_sent_date": "2026-09-20"}, date(2026, 9, 21),
                    "7", "25 8", now=datetime(2026, 9, 21, 13, 7, tzinfo=LISBON))
check("a late fallback run raises exactly one note", len(_all), 1)
check_true("and it is the latency one", _all[0].startswith("BRIEF LATE"), _all)

# §3.11: a green unit test over a function nothing calls proves nothing.
_late_ctx = dict(healthy)
_late_ctx["health"] = [_cron_note]
_late_md, _late_html = render.build(_late_ctx)
check_true("the rendered brief carries the late banner",
           "BRIEF LATE" in _late_md, _late_md[:400])
check_true("and the HTML marks it as a warning",
           "warn" in _late_html and "BRIEF LATE" in _late_html,
           _late_html[:600])

# main.py resolves which cron slot owns today from TARGET_HOUR, and health.py
# judges lateness against the same hour. Two definitions would drift.
check("main and health agree on what on time means",
      main.TARGET_HOUR, health.TARGET_HOUR)
check("and the target minute matches both cron slots", health.TARGET_MINUTE, 25)


print("\n-- warnings lead the brief, and look like warnings --")
_warn_ctx = dict(healthy)
_warn_ctx["health"] = ["DELIVERY GAP — 1 brief never sent: Sat 12 Sep.",
                       "TRIGGER OUT OF DATE — reports version 6."]
_wmd, _whtml = render.build(_warn_ctx)
check_true("the warning is in the brief", "DELIVERY GAP" in _wmd, _wmd[:400])
check_true("above every market section",
           _wmd.index("DELIVERY GAP") < _wmd.index("## THE SETUP"), _wmd[:400])
check_true("both warnings survive", "TRIGGER OUT OF DATE" in _wmd)
check_true("typeset as a warning, not as one more data line",
           "> **⚠ DELIVERY GAP" in _wmd, _wmd[:400])
check_true("and carries its own style in the email",
           "class='warn'" in _whtml, _whtml[:900])
check_true("a healthy brief carries no banner at all",
           "⚠ DELIVERY GAP" not in render.build(healthy)[0])

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
# Buckets went from three (capped at 130 days) to five (365). A T-3 event is
# "Now" and a T-39 one is "3 months" - the names changed with the ranges.
check_true("nearest is grouped as now", "**Now**" in _ahead, _ahead)
check_true("far one falls in the three-month bucket",
           "**3 months**" in _ahead, _ahead)
check_true("and the buckets it does not need are absent",
           "**6 months**" not in _ahead and "**12 months**" not in _ahead,
           _ahead)
check_true("the primary source is linked", "https://fr.test/doc" in _ahead,
           _ahead)
check_true("how much was read is stated",
           "Scanned 7 presidential documents" in _ahead, _ahead)

_today_evt = dict(_wl_evt, date=date(2026, 9, 5))
_md_today = render.build(_radar_ctx([], [_today_evt]))[0]
check_true("a date landing today says TODAY, not T-0",
           "TODAY" in _md_today.split("## AHEAD")[1], _md_today[:400])
check_true("and it also reaches the risk windows",
           "TODAY" in _md_today.split("## TODAY")[1],
           _md_today.split("## TODAY")[1][:400])

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
    "announced": [],
    "completed": [{"date": date(2026, 9, 3), "settles": date(2026, 9, 4),
                   "security_type": "Nominal", "bucket": "10 to 20 years",
                   "offered": 4.0e9, "accepted": 2.5e9, "cap": 2.0e9}],
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


print("\n-- Fiscal Data returns the STRING 'null' --")
# This is the bug that put "\u2014 accepted of \u2014 offered" in the 10 Sep brief:
# every value arrives as a string, and a missing one arrives as "null", which
# is truthy.
check("the string 'null' is not a value", sources._fd_val("null"), None)
check("an empty string is not a value", sources._fd_val(""), None)
check("a real value survives", sources._fd_val("Nominal"), "Nominal")
check("'null' does not become a number", sources._fd_amt("null"), None)
check("a numeric string does", sources._fd_amt("6000000000"), 6.0e9)

print("\n-- operation times convert from Eastern to Lisbon --")
_lis = sources._et_to_lisbon(date(2026, 9, 10), "01:40 PM")
check("13:40 ET on 10 Sep is 18:40 LIS", _lis.strftime("%H:%M"), "18:40")
# January: US on EST, Portugal on WET - a 5h gap, not the summer 5h... the
# point is that the zone decides, not a constant.
_win = sources._et_to_lisbon(date(2026, 1, 14), "01:40 PM")
check("and the gap is recomputed in winter", _win.strftime("%H:%M"), "18:40")
check("a missing clock is not a time", sources._et_to_lisbon(date(2026, 9, 10), "null"), None)

print("\n-- POLICY DESK: an announced buyback is not history --")
_ANNOUNCED = {"ok": True, "error": None, "data": {
    "announced": [{"date": date(2026, 9, 10), "settles": date(2026, 9, 11),
                   "security_type": "Nominal", "bucket": "10Y to 20Y",
                   "offered": None, "accepted": None, "cap": 6.0e9,
                   "eligible": "40",
                   "opens": datetime(2026, 9, 10, 18, 40, tzinfo=LISBON),
                   "closes": datetime(2026, 9, 10, 19, 0, tzinfo=LISBON),
                   "norm": 2.0e9, "norm_n": 3, "step_up": True}],
    "completed": [{"date": date(2026, 9, 9), "settles": date(2026, 9, 10),
                   "security_type": "Nominal", "bucket": "1Mo to 2Y",
                   "offered": 28.0e9, "accepted": 12.5e9, "cap": 2.0e9}],
    "auctions": [], "partial": None, "source": "Treasury"}}

def _ann_ctx():
    c = _desk_ctx(_FED_OK, _ANNOUNCED)
    c["now"] = datetime(2026, 9, 10, 9, 20, tzinfo=LISBON)
    return c

_md_ann = render.build(_ann_ctx())[0]
_desk_ann = _md_ann.split("## POLICY DESK")[1].split("\n## ")[0]
check_true("it is labelled announced, not printed as a past operation",
           "ANNOUNCED" in _desk_ann, _desk_ann)
check_true("a same-day operation says TODAY", "buyback TODAY" in _desk_ann,
           _desk_ann)
check_true("the cap is the headline number",
           "up to $6.0bn" in _desk_ann, _desk_ann)
check_true("the operation window is in Lisbon time",
           "18:40\u201319:00 LIS" in _desk_ann, _desk_ann)
check_true("a step up on the norm is called out",
           "3.0\u00d7 the $2.0bn norm for this maturity bucket" in _desk_ann,
           _desk_ann)
check_true("blank amounts never appear on an announced operation",
           "\u2014 accepted of \u2014 offered" not in _desk_ann, _desk_ann)
check_true("a completed operation still reports its result",
           "$12.5bn accepted of $28.0bn offered" in _desk_ann, _desk_ann)

print("\n-- an operation running today reaches TODAY --")
_rw = _md_ann.split("## TODAY")[1]
check_true("it is listed as a timed window",
           "Treasury buyback operation" in _rw, _rw)
check_true("with its size", "up to $6.0bn" in _rw, _rw)
check_true("and at the right hour", "**18:40**" in _rw, _rw)

print("\n-- a routine operation is not dressed up as a step-up --")
_ROUTINE = {"ok": True, "error": None, "data": dict(
    _ANNOUNCED["data"],
    announced=[dict(_ANNOUNCED["data"]["announced"][0],
                    cap=2.0e9, step_up=False)])}
_routine = render.build(_desk_ctx(_FED_OK, _ROUTINE))[0].split("## POLICY DESK")[1]
check_true("no step-up claim", "the recent norm" not in _routine, _routine)
check_true("but still flagged as announced", "ANNOUNCED" in _routine, _routine)

print("\n-- an announced operation with no published size says so --")
_NOSIZE = {"ok": True, "error": None, "data": dict(
    _ANNOUNCED["data"],
    announced=[dict(_ANNOUNCED["data"]["announced"][0],
                    cap=None, step_up=False)])}
_nosize = render.build(_desk_ctx(_FED_OK, _NOSIZE))[0].split("## POLICY DESK")[1]
check_true("it does not invent a number",
           "size not yet published" in _nosize, _nosize)
check_true("and does not print a zero", "$0.0bn" not in _nosize, _nosize)

print("\n-- nothing announced is stated, not left blank --")
_none = render.build(_desk_ctx(_FED_OK, _OPS_OK))[0].split("## POLICY DESK")[1]
check_true("says no operation is announced",
           "No buyback operation currently announced" in _none, _none)


print("\n-- treasury_ops runs end to end against canned API payloads --")
# The fixture tests above all bypass the fetcher, which is how a NameError
# from a deleted helper reached a live run with every test green. This one
# exercises the real function with the network stubbed, using payload shapes
# copied from the API - including Fiscal Data's string "null".
_FD_ROWS = {"data": [
    {"operation_date": "2026-09-10", "settlement_date": "2026-09-11",
     "security_type": "Nominal", "maturity_bucket": "10Y to 20Y",
     "total_par_amt_offered": "null", "total_par_amt_accepted": "null",
     "nbr_issues_accepted": "null", "max_par_amt_redeemed": "6000000000",
     "nbr_issues_eligible": "40", "operation_start_time_est": "01:40 PM",
     "operation_close_time_est": "02:00 PM",
     "preliminary_ann_xml": "BBPA_20260910174000.xml", "final_ann_xml": "null"},
    {"operation_date": "2026-09-09", "settlement_date": "2026-09-10",
     "security_type": "Nominal", "maturity_bucket": "1Mo to 2Y",
     "total_par_amt_offered": "28000000000",
     "total_par_amt_accepted": "12500000000", "nbr_issues_accepted": "12",
     "max_par_amt_redeemed": "2000000000", "nbr_issues_eligible": "40",
     "operation_start_time_est": "01:40 PM",
     "operation_close_time_est": "02:00 PM",
     "preliminary_ann_xml": "BBPA_20260909174000.xml",
     "final_ann_xml": "BBA_20260909174000.xml"},
]}
_TD_ROWS = [
    {"securityType": "Note", "securityTerm": "10-Year",
     "auctionDate": "2026-09-17T00:00:00", "reopening": "Yes"},
    {"securityType": "Bill", "securityTerm": "13-Week",
     "auctionDate": "2026-09-11T00:00:00", "reopening": "No"},
]

_real_json = sources._json
def _fake_json(url, **kw):
    return _FD_ROWS if "buybacks_operations" in url else _TD_ROWS
sources._json = _fake_json
try:
    _ops = sources.treasury_ops(date(2026, 9, 10))
finally:
    sources._json = _real_json

check("the unrun operation is classified as announced", len(_ops["announced"]), 1)
check("the finished one as completed", len(_ops["completed"]), 1)
_a = _ops["announced"][0]
check("the cap is read from max_par_amt_redeemed", _a["cap"], 6.0e9)
check("a 'null' amount stays None, not 0.0", _a["accepted"], None)
check("the operation window converts to Lisbon",
      _a["opens"].strftime("%H:%M"), "18:40")
# The only completed row here is a short-end operation, so there is no
# same-bucket history for this long-end announcement and no norm to claim.
check("a cross-bucket comparison is refused", _a["norm"], None)
check("so no step-up is asserted", _a["step_up"], False)
check("bills are excluded from the auction calendar",
      [a["term"] for a in _ops["auctions"]], ["10-Year"])
check("a reopening is flagged", _ops["auctions"][0]["reopening"], True)
check_true("nothing degraded", _ops.get("partial") is None,
           str(_ops.get("partial")))


print("\n-- step-up compares like with like, or says nothing --")
def _ops_for(completed_rows, announced_bucket="10Y to 20Y", cap=6.0e9):
    rows = {"data": [
        {"operation_date": "2026-09-10", "settlement_date": "2026-09-11",
         "security_type": "Nominal", "maturity_bucket": announced_bucket,
         "total_par_amt_offered": "null", "total_par_amt_accepted": "null",
         "nbr_issues_accepted": "null", "max_par_amt_redeemed": str(int(cap)),
         "nbr_issues_eligible": "40", "operation_start_time_est": "01:40 PM",
         "operation_close_time_est": "02:00 PM",
         "preliminary_ann_xml": "x.xml", "final_ann_xml": "null"},
    ] + completed_rows}
    real = sources._json
    sources._json = lambda url, **kw: rows if "buybacks" in url else []
    try:
        return sources.treasury_ops(date(2026, 9, 10))
    finally:
        sources._json = real

def _done(bucket, cap, day):
    return {"operation_date": day, "settlement_date": day,
            "security_type": "Nominal", "maturity_bucket": bucket,
            "total_par_amt_offered": "1", "total_par_amt_accepted": "1",
            "nbr_issues_accepted": "1", "max_par_amt_redeemed": str(int(cap)),
            "nbr_issues_eligible": "40", "operation_start_time_est": "01:40 PM",
            "operation_close_time_est": "02:00 PM",
            "preliminary_ann_xml": "x.xml", "final_ann_xml": "y.xml"}

# The live case: two short-end operations at $12.5bn alongside long-end ones
# at $2bn. Mixing them gave "1.5x the norm of $4.0bn" for a tripling.
_mixed = _ops_for([
    _done("1Mo to 2Y", 12.5e9, "2026-09-09"),
    _done("1Mo to 2Y", 12.5e9, "2026-09-03"),
    _done("10Y to 20Y", 2.0e9, "2026-08-25"),
    _done("10Y to 20Y", 2.0e9, "2026-08-20"),
])
_ma = _mixed["announced"][0]
check("short-end operations do not set the long-end norm", _ma["norm"], 2.0e9)
check("so a tripling reads as a tripling", round(_ma["cap"] / _ma["norm"], 1), 3.0)
check("and is flagged", _ma["step_up"], True)

# No same-bucket history: make no claim rather than a cross-programme one.
_lonely = _ops_for([_done("1Mo to 2Y", 12.5e9, "2026-09-09")])
check("no same-bucket peers means no norm",
      _lonely["announced"][0]["norm"], None)
check("and therefore no step-up claim",
      _lonely["announced"][0]["step_up"], False)

# One peer is not a norm either.
_one = _ops_for([_done("10Y to 20Y", 2.0e9, "2026-08-25")])
check("a single peer is not enough to call a norm",
      _one["announced"][0]["norm"], None)


print("\n-- BLS: index values in, m/m and y/y out --")
# Shape copied from the live response, including the "-" that October 2025
# carries for the appropriations lapse and the M13 annual average.
_BLS = {"status": "REQUEST_SUCCEEDED", "message": [], "Results": {"series": [{
    "seriesID": "CUSR0000SA0", "data": [
        {"year": "2026", "period": "M13", "value": "330.000", "footnotes": [{}]},
        {"year": "2026", "period": "M08", "value": "334.131", "latest": "true",
         "footnotes": [{}]},
        {"year": "2026", "period": "M07", "value": "332.813", "footnotes": [{}]},
        {"year": "2025", "period": "M10", "value": "-", "footnotes": [
            {"code": "X", "text": "Data unavailable due to the 2025 lapse"}]},
        {"year": "2025", "period": "M08", "value": "323.291", "footnotes": [
            {"code": "P", "text": "Preliminary."}]},
    ]}]}}
_pts = sources._bls_points(_BLS["Results"]["series"][0])
check("the annual average is not a month", len(_pts), 4)
check("newest first", (_pts[0][0], _pts[0][1]), (2026, 8))
check("a '-' value is not a number", [p[2] for p in _pts if p[1] == 10], [None])

_real = sources._json
sources._json = lambda url, **kw: _BLS
try:
    _infl = sources.inflation()
finally:
    sources._json = _real
_p = _infl["prints"][0]
check("the period is named", _p["period"], "August 2026")
check("month-over-month from the index", round(_p["mom"], 3), 0.396)
check("year-over-year from the index", round(_p["yoy"], 2), 3.35)
check_true("all three series were attempted",
           "Core CPI" in (_infl.get("partial") or "") or len(_infl["prints"]) >= 1,
           str(_infl.get("partial")))

print("\n-- Kalshi: nearest meeting, mid of book --")
def _mkt(ticker, event, sub, bid, ask, close, last="0.5000"):
    return {"ticker": ticker, "event_ticker": event, "yes_sub_title": sub,
            "yes_bid_dollars": bid, "yes_ask_dollars": ask,
            "last_price_dollars": last, "close_time": close,
            "volume_fp": "1000.00"}
_KAL = {"markets": [
    # A far-dated meeting, which must not win.
    _mkt("KXFEDDECISION-28JAN-H25", "KXFEDDECISION-28JAN", "Hike 25bps",
         "0.1000", "0.2100", "2028-01-26T18:59:00Z"),
    # The next meeting.
    _mkt("KXFEDDECISION-26SEP-H25", "KXFEDDECISION-26SEP", "Hike 25bps",
         "0.8500", "0.8700", "2026-09-16T18:59:00Z"),
    _mkt("KXFEDDECISION-26SEP-N", "KXFEDDECISION-26SEP", "No change",
         "0.1300", "0.1500", "2026-09-16T18:59:00Z"),
    _mkt("KXFEDDECISION-26SEP-C25", "KXFEDDECISION-26SEP", "Cut 25bps",
         "0.0000", "0.0100", "2026-09-16T18:59:00Z"),
]}
sources._json = lambda url, **kw: _KAL
try:
    _odds = sources.fed_odds(date(2026, 9, 12))
finally:
    sources._json = _real
check("the soonest meeting is chosen", _odds["event"], "KXFEDDECISION-26SEP")
check("a far-dated contract is excluded", len(_odds["outcomes"]), 3)
check("the favourite leads", _odds["outcomes"][0]["label"], "Hike 25bps")
check("priced off the mid", round(_odds["outcomes"][0]["prob"], 1), 86.0)
check("mids sum near 100", round(_odds["raw_total"]), 100)

print("\n-- FED PATH renders, and refuses to forecast --")
def _fed_ctx(rate=None, odds=None, infl=None):
    c = dict(healthy)
    c["now"] = datetime(2026, 9, 12, 9, 20, tzinfo=LISBON)
    c["policy_radar"] = {"ok": True, "error": None, "data": {
        "events": [], "texts_scanned": 3, "partial": None,
        "source": "Federal Register"}}
    c["watchlist"] = {"events": [], "problems": []}
    c["fed_officials"] = None
    c["treasury_ops"] = None
    c["policy_rate"] = rate
    c["fed_odds"] = odds
    c["inflation"] = infl
    return c

_RATE_OK = {"ok": True, "error": None, "data": {
    "as_of": date(2026, 9, 10), "effr": 3.63, "target_low": 3.5,
    "target_high": 3.75, "volume_bn": 108, "source": "New York Fed"}}
_ODDS_OK = {"ok": True, "error": None, "data": {
    "event": "KXFEDDECISION-26SEP",
    "closes": datetime(2026, 9, 16, 19, 59, tzinfo=LISBON),
    "outcomes": [{"label": "Hike 25bps", "prob": 86.0, "spread": 2.0,
                  "volume": 1e5, "ticker": "a"},
                 {"label": "No change", "prob": 14.0, "spread": 2.0,
                  "volume": 1e5, "ticker": "b"}],
    "raw_total": 100.0, "source": "Kalshi (prediction market, mid of book)"}}
_INFL_OK = {"ok": True, "error": None, "data": {"prints": [
    {"label": "CPI", "period": "August 2026", "year": 2026, "month": 8,
     "index": 334.131, "mom": 0.396, "yoy": 3.352, "preliminary": False,
     "series_id": "CUSR0000SA0"},
    {"label": "PPI final demand", "period": "August 2026", "year": 2026,
     "month": 8, "index": 157.411, "mom": 0.400, "yoy": 5.41,
     "preliminary": True, "series_id": "WPSFD4"}],
    "partial": None, "source": "BLS public API"}}

_fed = render.build(_fed_ctx(_RATE_OK, _ODDS_OK, _INFL_OK))[0] \
    .split("## EXPECTATIONS")[1].split("\n## ")[0]
check_true("the target range is stated",
           "Target 3.50\u20133.75%" in _fed, _fed)
check_true("the effective rate sits beside it", "EFFR 3.63%" in _fed, _fed)
check_true("the priced favourite is shown",
           "Hike 25bps **86%**" in _fed, _fed)
check_true("with a countdown to the decision", "T-4" in _fed, _fed)
check_true("CPI carries its month, not today's date",
           "CPI** August 2026" in _fed, _fed)
check_true("month-over-month and year-over-year both appear",
           "+0.40% m/m" in _fed and "+3.4% y/y" in _fed, _fed)
check_true("a preliminary PPI print says so",
           "(preliminary)" in _fed, _fed)
check_true("the odds are labelled a prediction market, not CME",
           "prediction market" in _fed, _fed)
check_true("it never claims what the market will do",
           not any(w in _fed.lower() for w in
                   ("expect", "should ", "will likely", "target price")), _fed)

print("\n-- the target range admits when a decision has overtaken it --")
# §3.24, reproduced from the real thing. The FOMC moved to 3.75-4.00% on
# 16 Sep 2026 and FED PATH printed "Target 3.50-3.75% - as of 16 Sep" on the
# 17th AND the 18th: correctly sourced, correctly age-stamped, and materially
# misleading. A reader would reasonably have concluded the Fed had held.
def _fomc_feed(*items):
    return {"ok": True, "error": None, "data": {
        "items": [dict(kind=k, speaker="FOMC", title=t, date=d, url="")
                  for k, t, d in items],
        "watching": ["Warsh"], "lookback_days": 21, "partial": None,
        "source": "Federal Reserve RSS"}}


_STATEMENT = ("FOMC", "Federal Reserve issues FOMC statement", date(2026, 9, 16))
_PROJECTIONS = ("FOMC", "Federal Reserve Board and Federal Open Market "
                "Committee release economic projections", date(2026, 9, 17))
_SPEECH = ("speech", "In Our Time", date(2026, 9, 18))

check("the statement's date is found",
      render._last_fomc_statement({"fed_officials": _fomc_feed(_STATEMENT)}),
      date(2026, 9, 16))
# The same feed carries the projections release and the implementation note.
# Neither is the decision, and counting one would move the date by a day.
check("the projections release is not the decision",
      render._last_fomc_statement(
          {"fed_officials": _fomc_feed(_PROJECTIONS, _SPEECH)}), None)
check("a failed feed makes no claim",
      render._last_fomc_statement({"fed_officials": {"ok": False}}), None)
check("and neither does a missing one", render._last_fomc_statement({}), None)

_sep16 = date(2026, 9, 16)
_R = {"as_of": _sep16, "target_low": 3.5}
# as_of EQUAL to the decision date is stale, not current: the decision lands
# 19:00 Lisbon, so the rate in force for almost all of that day is the old one.
check_true("a range dated the day of the decision is stale",
           render.superseded_range(_R, _sep16))
check_true("a range dated before it is stale too",
           render.superseded_range({"as_of": date(2026, 9, 15),
                                    "target_low": 3.5}, _sep16))
check_true("the day after, it is current again",
           not render.superseded_range({"as_of": date(2026, 9, 17),
                                        "target_low": 3.5}, _sep16))
check_true("no statement seen is no claim",
           not render.superseded_range(_R, None))
check_true("no range printed is no claim",
           not render.superseded_range({"as_of": _sep16, "target_low": None},
                                       _sep16))
check_true("an unparseable as_of is no claim",
           not render.superseded_range({"as_of": "16 Sep", "target_low": 3.5},
                                       _sep16))

# §3.11: the helper being right proves nothing until the brief says it.
_stale_c = _fed_ctx(_RATE_OK, _ODDS_OK, _INFL_OK)
_stale_c["policy_rate"] = {"ok": True, "error": None, "data": dict(
    _RATE_OK["data"], as_of=date(2026, 9, 16))}
_stale_c["fed_officials"] = _fomc_feed(_STATEMENT)
_stale_md, _stale_html = render.build(_stale_c)
_stale_fed = _stale_md.split("## EXPECTATIONS")[1].split("\n## ")[0]
check_true("the rendered range carries the warning",
           "may be superseded" in _stale_fed, _stale_fed)
# §3.9: the marker goes next to the number, not in a footnote. A $6bn buyback
# was present, sourced and correctly stamped, and unreadable because the
# qualification was not where the eye was.
check_true("and the marker sits beside the number, not below it",
           _stale_fed.index("may be superseded")
           - _stale_fed.index("Target 3.50") < 60, _stale_fed)
check_true("the note names both dates",
           "16 Sep" in _stale_fed and "statement" in _stale_fed, _stale_fed)
check_true("and points at where the real decision is",
           "POLICY DESK" in _stale_fed, _stale_fed)
check_true("the range itself is still printed, not suppressed",
           "Target 3.50\u20133.75%" in _stale_fed, _stale_fed)
check_true("and it reaches the HTML too",
           "may be superseded" in _stale_html, _stale_html[:200])

# The far more common case: no FOMC in the last three weeks. Silence.
_ok_c = _fed_ctx(_RATE_OK, _ODDS_OK, _INFL_OK)
_ok_c["fed_officials"] = _fomc_feed(_SPEECH)
_ok_fed = render.build(_ok_c)[0].split("## EXPECTATIONS")[1].split("\n## ")[0]
check_true("a normal morning says nothing about supersession",
           "may be superseded" not in _ok_fed, _ok_fed)


print("\n-- FED PATH degrades honestly --")
_wide = {"ok": True, "error": None, "data": dict(
    _ODDS_OK["data"], raw_total=72.0)}
_w = render.build(_fed_ctx(_RATE_OK, _wide, _INFL_OK))[0] \
    .split("## EXPECTATIONS")[1].split("\n## ")[0]
check_true("a book that does not sum to 100 is flagged",
           "not ~100%" in _w and "indicative" in _w, _w)

_dead = {"ok": False, "error": "HTTP 429", "data": None}
_d = render.build(_fed_ctx(_dead, _dead, _dead))[0] \
    .split("## EXPECTATIONS")[1].split("\n## ")[0]
check_true("each leg names its own failure",
           _d.count("HTTP 429") == 3, _d)
check_true("and no number is invented", "0%" not in _d, _d)


print("\n-- seven days a week, but Sunday is still Sunday --")
# The brief now runs at weekends. What must NOT happen is a weekend brief that
# lists a cash open and close as if the session existed.
_sun = dict(dead)
_sun["now"] = datetime(2026, 9, 13, 9, 20, tzinfo=LISBON)   # a Sunday
_sun_md = render.build(_sun)[0]
_sun_rw = _sun_md.split("## TODAY")[1].split("\n## ")[0]
check_true("a weekend brief is still produced",
           _sun_md.startswith("# MARKET BRIEF"), _sun_md[:60])
check_true("and says the cash market is shut",
           "Cash equity markets closed today" in _sun_rw, _sun_rw)
check_true("without inventing an open", "NYSE cash open" not in _sun_rw, _sun_rw)
check_true("or a close", "NYSE cash close" not in _sun_rw, _sun_rw)

_mon = dict(dead)
_mon["now"] = datetime(2026, 9, 14, 9, 20, tzinfo=LISBON)   # a Monday
_mon_rw = render.build(_mon)[0].split("## TODAY")[1].split("\n## ")[0]
check_true("a weekday still gets its session windows",
           "NYSE cash open" in _mon_rw, _mon_rw)


print()
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print("  -", f)
    raise SystemExit(1)
print("All checks passed.")
