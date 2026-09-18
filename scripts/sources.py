"""
Data source adapters for the daily market brief.

Every fetcher here obeys three rules:

1. It returns real data or it raises. It never returns a plausible-looking
   placeholder. A step that cannot be sourced is reported as unavailable.
2. It carries its own provenance (where the number came from, and as-of when)
   so the renderer can label freshness honestly.
3. It never blocks the brief. Callers wrap each fetcher in `safe()`.

Sources deliberately NOT used, and why:
  coinglass.com / coinalyze.net / theblock.co  - client-side render, return
      empty tables and literal 0% placeholders that read as real data.
  deribit.com/statistics                       - JS shell.
  cmegroup.com FedWatch                        - QuikStrike iframe, no data.
Use the documented APIs instead, which is what this module does.
"""

from __future__ import annotations

import os
import re
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests

LISBON = ZoneInfo("Europe/Lisbon")
UTC = timezone.utc

FF_THIS_WEEK = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
# ForexFactory publishes only the current week. `ff_calendar_nextweek.json`
# was requested for weeks and 404s every time - a probe against a runner
# confirmed it, and it appears never to have existed. The forward view is
# therefore limited to the remainder of this week, which the brief states.
KRAKEN_TICKER = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD,ETHUSD,SOLUSD"
FNG = "https://api.alternative.me/fng/?limit=8"
# Farside 403s datacenter IPs regardless of headers - re-confirmed by probe.
# TFTC republishes the same underlying data (SoSoValue) as open JSON under
# CC BY 4.0, with a per-fund breakdown and an `updatedThrough` freshness
# field Farside never gave us. Attribution is a licence condition.
TFTC_BTC_FLOWS = "https://www.tftc.io/bitcoin-etf-flows/data.json"
DERIBIT_TICKER = "https://www.deribit.com/api/v2/public/ticker"
DERIBIT_BOOK = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
COINGECKO_GLOBAL = "https://api.coingecko.com/api/v3/global"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

UA = "Mozilla/5.0 (compatible; market-brief/1.0; +https://github.com/kabil1101/Kab)"
HEADERS = {"User-Agent": UA, "Accept": "*/*"}

# Farside rejects a plain API-style user agent with 403. HTML pages get a
# browser-shaped header set instead.
BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0.0.0 Safari/537.36"),
    "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
               "image/avif,image/webp,*/*;q=0.8"),
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://farside.co.uk/",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
}
TIMEOUT = 30


def _reason(exc) -> str:
    """A short, human-readable cause. The full traceback goes to the run log;
    the brief itself gets one clause, because a wall of urllib3 text in an
    email body hides the one thing the reader needs - which source is down."""
    resp = getattr(exc, "response", None)
    if resp is not None and getattr(resp, "status_code", None):
        return f"HTTP {resp.status_code}"
    if isinstance(exc, requests.Timeout):
        return "timeout"
    if isinstance(exc, requests.ConnectionError):
        return "connection failed"
    if isinstance(exc, RuntimeError) and str(exc):
        return str(exc)      # already compact, e.g. re-wrapped from _get
    return type(exc).__name__


def _get(url: str, *, params=None, tries: int = 3, headers=None):
    """GET with bounded retries. Raises a compact error on final failure."""
    last = None
    for _ in range(tries):
        try:
            r = requests.get(url, params=params, headers=headers or HEADERS,
                             timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except Exception as exc:  # noqa: BLE001 - caller decides
            last = exc
    raise RuntimeError(f"{urlparse(url).netloc}: {_reason(last)}")


def _json(url: str, *, params=None):
    return _get(url, params=params).json()


# ---------------------------------------------------------------- calendar

def _parse_ff(rows, seen):
    out = []
    for e in rows:
        raw = e.get("date")
        if not raw:
            continue
        try:
            # ISO 8601 carrying a US Eastern offset (-04:00 EDT / -05:00 EST).
            # Derive the offset from the string; never assume a fixed ET gap,
            # because the US and EU switch DST on different dates.
            dt = datetime.fromisoformat(raw)
        except ValueError:
            continue
        if dt.tzinfo is None:
            continue
        key = (e.get("title"), e.get("country"), raw)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "title": e.get("title") or "",
                "country": (e.get("country") or "").upper(),
                "impact": (e.get("impact") or "").strip(),
                "forecast": (e.get("forecast") or "").strip(),
                "previous": (e.get("previous") or "").strip(),
                "dt_lis": dt.astimezone(LISBON),
            }
        )
    return out


def calendar():
    """ForexFactory weekly feeds. Schedule-only: there is no `actual` field.

    The this-week feed ends Friday, so from Wednesday on we also pull next
    week or the forward view collapses on Thu/Fri.
    """
    import sys
    from collections import Counter

    seen: set = set()
    events = _parse_ff(_json(FF_THIS_WEEK), seen)
    this_count = len(events)
    today = datetime.now(LISBON).date()

    # No next-week fetch: ForexFactory publishes only the current week.
    events.sort(key=lambda e: e["dt_lis"])

    impacts = Counter(e["impact"] for e in events)
    print(f"  calendar: {this_count} events this week; impacts={dict(impacts)}",
          file=sys.stderr)

    if os.environ.get("BRIEF_DEBUG"):
        for e in events:
            if e["dt_lis"].date() == today:
                print(f"    [debug] {e['dt_lis']:%H:%M} {e['country']:<4} "
                      f"{e['impact']:<8} {e['title']}", file=sys.stderr)

    return {
        "events": events,
        # Kept for the renderer's benefit: the forward view genuinely stops at
        # the end of this week, and saying so beats an empty section that
        # reads as "nothing scheduled".
        "week_only": True,
        "source": "ForexFactory (nfs.faireconomy.media)",
    }


# ------------------------------------------------------------------ crypto

KRAKEN_KEYS = [("XXBTZUSD", "BTC"), ("XETHZUSD", "ETH"), ("SOLUSD", "SOL")]


def crypto():
    """Kraken ticker. Keys are remapped server-side, so match by key, not by
    the order we requested the pairs in."""
    data = _json(KRAKEN_TICKER)
    if data.get("error"):
        raise RuntimeError(f"Kraken error: {data['error']}")
    result = data["result"]
    out = []
    for key, sym in KRAKEN_KEYS:
        if key not in result:
            continue
        t = result[key]
        last = float(t["c"][0])
        # `o` is the opening price of the CURRENT UTC DAY (a scalar), not a
        # rolling 24h open. So this percentage is "since 00:00 UTC" and must
        # be labelled as such - pairing it with the rolling 24h high/low would
        # mix two different windows.
        day_open = float(t["o"])
        out.append(
            {
                "symbol": sym,
                "last": last,
                "day_open": day_open,
                "pct_since_utc_midnight": (last - day_open) / day_open * 100.0,
                "high_24h": float(t["h"][1]),
                "low_24h": float(t["l"][1]),
                "vol_24h": float(t["v"][1]),
                "vwap_24h": float(t["p"][1]),
            }
        )
    if not out:
        raise RuntimeError("Kraken returned no recognised pairs")
    return {"pairs": out, "source": "Kraken public ticker"}


# --------------------------------------------------------------- sentiment

def fear_greed():
    """alternative.me Fear & Greed. Attribution to alternative.me is required
    by their terms and is emitted by the renderer."""
    data = _json(FNG)["data"]
    def norm(row):
        return {
            "value": int(row["value"]),
            "classification": row["value_classification"],
            "at": datetime.fromtimestamp(int(row["timestamp"]), UTC),
        }
    today = norm(data[0])
    week_ago = norm(data[7]) if len(data) > 7 else None
    return {
        "today": today,
        "week_ago": week_ago,
        "source": "alternative.me",
    }


# ------------------------------------------------------------------- flows

def etf_flows_btc():
    """US spot Bitcoin ETF daily net flows, from TFTC's open dataset.

    Farside was the original source and 403s datacenter IPs regardless of
    headers. TFTC republishes the same underlying SoSoValue data as open JSON
    under CC BY 4.0, with a per-fund breakdown and an `updatedThrough` field
    that lets the brief say how fresh the figures actually are.

    Amounts arrive in whole USD and are converted to US$m, the unit the brief
    has always printed.
    """
    data = _json(TFTC_BTC_FLOWS)
    days = data.get("days") or []
    if not days:
        raise RuntimeError("dataset carried no days")

    rows = [d for d in days if d.get("netFlowUsd") is not None]
    if not rows:
        raise RuntimeError("no day carried a net flow")
    rows.sort(key=lambda d: d["date"])

    def to_m(v):
        return None if v is None else v / 1e6

    recent = []
    for d in rows[-6:]:
        per = d.get("perEtfUsd") or {}
        recent.append({
            "date": date.fromisoformat(d["date"]),
            "total": to_m(d["netFlowUsd"]),
            "ibit": to_m(per.get("IBIT")),
            "fbtc": to_m(per.get("FBTC")),
            "etha": None,
        })

    return {
        "latest_date": recent[-1]["date"],
        "latest_total": recent[-1]["total"],
        "recent": recent,
        "updated_through": data.get("updatedThrough"),
        # CC BY 4.0 requires attribution, and the brief credits its sources
        # anyway.
        "source": data.get("attribution") or "TFTC (CC BY 4.0)",
    }


def perp_stats(currency: str = "BTC"):
    """Funding and open interest for the perpetual, from Deribit.

    Binance was the obvious venue and returns HTTP 451 to US-hosted runners,
    so it cannot serve this job at all. Deribit is already reached
    successfully by the options fetcher, and a single ticker call carries both
    figures. This is one venue, not an aggregate across exchanges, and the
    brief labels it that way - an aggregate would need a paid provider.
    """
    inst = f"{currency}-PERPETUAL"
    r = _json(DERIBIT_TICKER, params={"instrument_name": inst})
    res = r.get("result")
    if not res:
        raise RuntimeError(f"no result for {inst}")

    stats = res.get("stats") or {}
    return {
        "instrument": inst,
        # funding_8h is a rate, e.g. 0.0001 = 0.01% per 8h.
        "funding_8h": res.get("funding_8h"),
        "current_funding": res.get("current_funding"),
        "open_interest": res.get("open_interest"),
        "index_price": res.get("index_price"),
        # Both already in the ticker payload this call has always made, so
        # basis costs nothing. Funding is the rate for the LAST interval and
        # lags; basis is where the perp is trading against the index right
        # now. The brief labels which is which, because two numbers that look
        # alike and mean different things is the $6bn failure in miniature.
        "mark_price": res.get("mark_price"),
        "last_price": res.get("last_price"),
        "volume_24h_usd": stats.get("volume_usd"),
        "source": "Deribit (single venue)",
    }


# ----------------------------------------------------------------- options

_INSTRUMENT = re.compile(r"^(?P<ccy>[A-Z]+)-(?P<exp>\d{1,2}[A-Z]{3}\d{2})-(?P<strike>\d+(?:\.\d+)?)-(?P<kind>[CP])$")


def _max_pain(by_strike):
    """Settlement strike that minimises total intrinsic value paid to option
    holders. by_strike maps strike -> {"C": oi, "P": oi}."""
    strikes = sorted(by_strike)
    best, best_val = None, None
    for settle in strikes:
        total = 0.0
        for k, oi in by_strike.items():
            if settle > k:
                total += oi.get("C", 0.0) * (settle - k)
            elif settle < k:
                total += oi.get("P", 0.0) * (k - settle)
        if best_val is None or total < best_val:
            best, best_val = settle, total
    return best


def _is_monthly(d: date) -> bool:
    """Deribit monthlies are the last Friday of the month."""
    return d.weekday() == 4 and (d + timedelta(days=7)).month != d.month


def options(currency: str = "BTC"):
    """Deribit public REST. No API key required.

    get_book_summary_by_currency returns one row per live instrument with its
    open interest, which is everything max pain needs. This is the documented
    replacement for the JS-only statistics page.
    """
    data = _json(DERIBIT_BOOK, params={"currency": currency, "kind": "option"})
    rows = data.get("result") or []
    if not rows:
        raise RuntimeError("Deribit returned no option rows")

    expiries: dict = {}
    underlying = None
    for r in rows:
        m = _INSTRUMENT.match(r.get("instrument_name", ""))
        if not m:
            continue
        oi = r.get("open_interest")
        if not oi:
            continue
        try:
            exp = datetime.strptime(m.group("exp"), "%d%b%y").date()
        except ValueError:
            continue
        strike = float(m.group("strike"))
        kind = m.group("kind")
        expiries.setdefault(exp, {}).setdefault(strike, {}).setdefault(kind, 0.0)
        expiries[exp][strike][kind] += float(oi)
        if underlying is None and r.get("underlying_price"):
            underlying = float(r["underlying_price"])

    if not expiries:
        raise RuntimeError("Deribit rows carried no parseable instruments")

    today = datetime.now(LISBON).date()
    future = sorted(e for e in expiries if e >= today)
    if not future:
        raise RuntimeError("no live expiries")

    def summarise(exp):
        by_strike = expiries[exp]
        calls = {k: v.get("C", 0.0) for k, v in by_strike.items()}
        puts = {k: v.get("P", 0.0) for k, v in by_strike.items()}
        top_call = max(calls, key=calls.get) if any(calls.values()) else None
        top_put = max(puts, key=puts.get) if any(puts.values()) else None
        total_c = sum(calls.values())
        total_p = sum(puts.values())

        def top3(book):
            """The three strikes carrying most open interest, biggest first.

            Capped at three per side deliberately. These are fetched numbers,
            not a view: "most open interest sits at 85k" is data, "BTC will
            pin to 85k" is a claim and stays banned (D3, D9).
            """
            live = [(k, v) for k, v in book.items() if v]
            return sorted(live, key=lambda kv: kv[1], reverse=True)[:3]

        return {
            "expiry": exp,
            "max_pain": _max_pain(by_strike),
            "top_call_strike": top_call,
            "top_call_oi": calls.get(top_call),
            "top_put_strike": top_put,
            "top_put_oi": puts.get(top_put),
            "top_calls": top3(calls),
            "top_puts": top3(puts),
            "put_call_oi_ratio": (total_p / total_c) if total_c else None,
            "total_oi": total_c + total_p,
        }

    nearest = summarise(future[0])
    monthly_exp = next((e for e in future if _is_monthly(e)), None)
    monthly = summarise(monthly_exp) if monthly_exp else None

    return {
        "currency": currency,
        "underlying": underlying,
        "nearest": nearest,
        "monthly": monthly,
        "source": "Deribit public API",
    }


# ------------------------------------------------------------- cross-asset

YAHOO_SYMBOLS = [
    ("DX-Y.NYB", "DXY"),
    ("^TNX", "US 10Y"),
    ("GC=F", "Gold"),
    ("CL=F", "WTI"),
    ("^VIX", "VIX"),
    ("ES=F", "S&P 500 fut"),
    ("NQ=F", "Nasdaq fut"),
]


def _yahoo_quote(symbol: str):
    data = _json(YAHOO_CHART.format(symbol=symbol), params={"range": "5d", "interval": "1d"})
    res = (data.get("chart") or {}).get("result")
    if not res:
        raise RuntimeError("no chart result")
    meta = res[0].get("meta") or {}
    last = meta.get("regularMarketPrice")
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    if last is None:
        raise RuntimeError("no price in meta")
    last = float(last)
    # ^TNX has historically been published as yield x10. Guard rather than
    # assume: a 10y Treasury yield above 20% is not a real reading.
    if symbol == "^TNX" and last > 20:
        last /= 10.0
        if prev:
            prev = float(prev) / 10.0
    chg = None
    if prev:
        prev = float(prev)
        chg = (last - prev) / prev * 100.0
    ts = meta.get("regularMarketTime")
    return {
        "last": last,
        "pct_change": chg,
        "as_of": datetime.fromtimestamp(int(ts), UTC).astimezone(LISBON) if ts else None,
    }


def cross_asset():
    out, errs = {}, {}
    for symbol, label in YAHOO_SYMBOLS:
        try:
            out[label] = _yahoo_quote(symbol)
        except Exception as exc:  # noqa: BLE001
            errs[label] = str(exc)
    if not out:
        first = next(iter(errs.values()), "unknown")
        raise RuntimeError(
            f"all {len(errs)} quotes failed (first: {first})")
    return {"quotes": out, "errors": errs, "source": "Yahoo Finance chart API"}


def coingecko_global():
    """Market cap, dominance, and the stablecoin pair.

    Probe round 17 settled the stablecoin question at zero cost: `usdt` and
    `usdc` are already in the `market_cap_percentage` block of the call this
    function has always made, so no second endpoint is needed.

    Supply is derived from total market cap rather than fetched, and D24 is
    why both are returned. **Dominance is a ratio: it rises when the
    denominator falls.** A dominance spike during a selloff is mostly
    arithmetic, and printing it alone hands the reader a risk-off signal that
    is sometimes just a falling market wearing a costume.
    """
    d = _json(COINGECKO_GLOBAL)["data"]
    pct = d["market_cap_percentage"]
    total = d["total_market_cap"]["usd"]
    usdt, usdc = pct.get("usdt"), pct.get("usdc")
    stable_pct = sum(v for v in (usdt, usdc) if v is not None) or None
    return {
        "total_mcap_usd": total,
        "mcap_change_24h_pct": d.get("market_cap_change_percentage_24h_usd"),
        "btc_dominance": pct.get("btc"),
        "eth_dominance": pct.get("eth"),
        "usdt_dominance": usdt,
        "usdc_dominance": usdc,
        "stable_dominance": stable_pct,
        "stable_supply_usd": (total * stable_pct / 100.0
                              if stable_pct is not None and total else None),
        "source": "CoinGecko /api/v3/global",
    }


# ------------------------------------------------------------ policy radar

FR_DOCS = "https://www.federalregister.gov/api/v1/documents.json"

# Probed from a runner before any of this was written, and the probe changed
# the design twice:
#   - `effective_on` is populated for 0 of 21 recent presidential documents,
#     so the structured field is useless for exactly the documents that move
#     markets. Rules and notices DO carry it, which is why they get a separate,
#     cheaper query below.
#   - `conditions[comments_close_on]` is not a filterable condition (HTTP 400).
# So a proclamation's effective date has to be read out of its prose. The cue
# phrases turned out to be near-boilerplate: "entered for consumption, or
# withdrawn from warehouse for consumption, on or after 12:01 a.m. eastern
# time on August 19, 2026".

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")
_DATE_RX = re.compile(rf"\b({MONTHS})\s+(\d{{1,2}}),\s+(20\d{{2}})\b")

# A date only counts if one of these appears just before it. Without this the
# regex mostly finds citations to prior orders.
# Mapped to the word the brief prints, because "expires on 1 November" and
# "effective 1 November" are opposite trades.
_CUES = {
    "shall expire": "expires",
    "expires on": "expires",
    "shall terminate": "expires",
    "no later than": "deadline",
    "on or after": "effective",
    "entered for consumption": "effective",
    "withdrawn from warehouse": "effective",
    "effective as of": "effective",
    "effective with respect to": "effective",
    "shall take effect": "effective",
    "takes effect": "effective",
    "beginning on": "effective",
}

# The citation form "Executive Order 14105 of August 9, 2023" and the Federal
# Register's own issue header both put a date next to words that would
# otherwise look like cues. Anything matching these right before the date is
# a reference to another document, not a deadline.
_CITE_RX = re.compile(
    r"(?:Executive Order|Proclamation|Notice|Determination|Memorandum|"
    r"Order|E\.?O\.?)\s*(?:No\.?\s*)?[\d\-]*\s*of\s*$", re.I)

# Titles worth reading the text of. A presidential document about renaming a
# lake is not a market event; one about duties, sanctions or export controls
# is. Presidential documents are few and already high-signal, so this tier can
# afford to be broad.
_MARKET_WORDS = (
    "tariff", "duty", "duties", "import", "export", "trade", "sanction",
    "embargo", "quota", "steel", "aluminum", "aluminium", "copper",
    "semiconductor", "chip", "polysilicon", "critical mineral", "energy",
    "petroleum", "oil", "emergency", "china", "section 232", "section 301",
    "currency", "crypto", "digital asset",
)

# The second pass reads EVERY agency's rules, thousands a month, so the broad
# tier is useless there - the first live run surfaced a marine-mammal permit
# (matched "oil"), a customs filing-system upgrade ("export") and a trademark
# classification notice ("trade" inside "Trademark"). These are the words that
# only appear when something actually moves a price.
_ACTION_WORDS = (
    "tariff", "duty", "duties", "sanction", "embargo", "quota",
    "export control", "export controls", "entity list",
    "section 232", "section 301", "countermeasure",
)

# Trade-remedy paperwork matches the words above and is pure noise for a macro
# reader: dozens of routine antidumping notices a week, none of them a market
# event.
_NOISE_WORDS = (
    "antidumping", "countervailing", "administrative review",
    "preliminary results", "final results", "postponement",
    "initiation of", "opportunity to request", "rescission",
    "sunset review", "combined notice of filings",
    # Annual renewals of an existing national emergency. They match on
    # "emergency" and there are a lot of them - Lebanon, Brazil, Mali and a
    # dozen more each year - but they announce no new date, so every one of
    # them would burn a text fetch out of the budget below and return nothing.
    # A NEW emergency is a different document and still gets through.
    "continuation of the national emergency",
    "continuation of the exercise",
)


def _title_rx(words):
    """Whole-word matcher, tolerant of a plural.

    Substring matching put "International Trademark Classification Changes"
    into the first live brief, because "trade" is inside "Trademark". Word
    boundaries fix that; the optional plural is what keeps "Adjusting Imports
    of Polysilicon" matching "import".
    """
    parts = [re.escape(w) if " " in w else rf"{re.escape(w)}(?:s|es)?"
             for w in words]
    return re.compile(r"\b(?:" + "|".join(parts) + r")\b", re.I)


_MARKET_RX = _title_rx(_MARKET_WORDS)
_ACTION_RX = _title_rx(_ACTION_WORDS)


def _fr_relevant(title: str, *, narrow: bool = False) -> bool:
    """Whether a document is worth the reader's attention.

    `narrow` applies the tighter word list used for the all-agency pass.
    """
    low = (title or "").lower()
    if any(n in low for n in _NOISE_WORDS):
        return False
    return bool((_ACTION_RX if narrow else _MARKET_RX).search(low))


def _extract_dates(text: str, not_before: date):
    """Future dates in a document's prose that a cue phrase marks as operative.

    Returns [(date, snippet)], nearest first. Requiring BOTH a cue and a date
    still ahead is what makes this safe to print: every citation to a previous
    order points backwards, so the date filter removes them even when the
    wording is ambiguous.
    """
    flat = " ".join((text or "").split())
    found: dict[date, str] = {}
    for m in _DATE_RX.finditer(flat):
        before = flat[max(0, m.start() - 140):m.start()]
        if _CITE_RX.search(before):
            continue
        low = before.lower()
        hits = [lab for cue, lab in _CUES.items() if cue in low]
        if not hits:
            continue
        try:
            when = datetime.strptime(
                f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date()
        except ValueError:
            continue
        if when < not_before:
            continue
        # "expires" and "deadline" are more specific claims than "effective",
        # which is the catch-all, so a clause carrying both reports the
        # narrower one.
        label = next((l for l in ("expires", "deadline") if l in hits),
                     "effective")
        found.setdefault(when, label)
    return sorted(found.items())


def policy_radar(today: date, lookback_days: int = 90,
                 horizon_days: int = 400, max_texts: int = 30) -> dict:
    """Dated US policy actions still ahead, from the Federal Register.

    Two passes, because the Register stores the two kinds of date differently:

      1. Presidential documents (proclamations, executive orders) published in
         the last `lookback_days`, whose effective dates are read out of the
         document text.
      2. Rules and notices with a future `effective_on`, which is structured
         and needs no text fetch.

    Neither pass predicts an *unscheduled* announcement - nothing free does.
    What it catches is the large class of actions that are signed on one day
    and bite on a later one, which is the part that can be prepared for.
    """
    events, notes = [], []
    horizon = today + timedelta(days=horizon_days)

    # --- pass 1: presidential documents, dates read from the prose
    scanned = 0
    try:
        data = _json(FR_DOCS, params={
            "per_page": 60,
            "order": "newest",
            "fields[]": ["title", "publication_date", "document_number",
                         "raw_text_url", "html_url", "type"],
            "conditions[type][]": "PRESDOCU",
            "conditions[publication_date][gte]":
                (today - timedelta(days=lookback_days)).isoformat(),
        })
        docs = [d for d in (data.get("results") or [])
                if _fr_relevant(d.get("title"))]
        for doc in docs[:max_texts]:
            url = doc.get("raw_text_url")
            if not url:
                continue
            try:
                text = _get(url, tries=2).text
            except Exception:  # noqa: BLE001 - one document, not the section
                continue
            scanned += 1
            for when, label in _extract_dates(text, today):
                if when > horizon:
                    continue
                events.append({
                    "date": when,
                    "title": " ".join((doc.get("title") or "").split()),
                    "kind": "presidential",
                    "label": label,
                    "url": doc.get("html_url"),
                    "signed": doc.get("publication_date"),
                })
    except Exception as exc:  # noqa: BLE001
        notes.append(f"presidential pass: {_reason(exc)}")

    # --- pass 2: rules and notices carrying a structured effective date
    try:
        data = _json(FR_DOCS, params={
            "per_page": 100,
            "order": "effective_date",
            "fields[]": ["title", "effective_on", "html_url", "type",
                         "agencies"],
            "conditions[effective_date][gte]": today.isoformat(),
        })
        for doc in (data.get("results") or []):
            raw = doc.get("effective_on")
            if not raw or not _fr_relevant(doc.get("title"), narrow=True):
                continue
            try:
                when = date.fromisoformat(raw)
            except ValueError:
                continue
            if when < today or when > horizon:
                continue
            agencies = [a.get("name") for a in (doc.get("agencies") or [])
                        if isinstance(a, dict) and a.get("name")]
            events.append({
                "date": when,
                "title": " ".join((doc.get("title") or "").split()),
                "kind": "rule",
                "label": "effective",
                "url": doc.get("html_url"),
                "agency": agencies[0] if agencies else None,
            })
    except Exception as exc:  # noqa: BLE001
        notes.append(f"rule pass: {_reason(exc)}")

    if notes and not events:
        raise RuntimeError("; ".join(notes))

    # Same action often appears as several near-identical proclamations
    # (the Canada duties landed as three on one day). Collapse on date+title.
    seen, unique = set(), []
    for e in sorted(events, key=lambda e: (e["date"], e["title"])):
        key = (e["date"], e["title"][:60].lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)

    return {"events": unique, "texts_scanned": scanned,
            "partial": "; ".join(notes) or None,
            "source": "Federal Register"}


# ------------------------------------------------------- policy desk: people

# Probed round 7-9. Three things came out of it that shaped this code:
#   - Fed feed item titles are "Speaker, Subject" - "Warsh, In Our Time" -
#     so filtering by person needs nothing cleverer than a split on the comma.
#   - Every value is wrapped in CDATA, which is why the first probe printed
#     empty dates: a naive tag-stripping regex eats <![CDATA[...]]> whole.
#     ElementTree handles it, so this parses XML as XML.
#   - Treasury publishes NO usable press feed. home.treasury.gov/rss.xml
#     answers 200 but carries careers pages and SSBCI FAQs; the documented
#     /rss/press.xml and the Drupal /feed paths all 404. So the Treasury
#     secretary is tracked through his ACTIONS - buybacks, auctions, refunding
#     - rather than his remarks, and the brief says so rather than scraping a
#     minified HTML page that would break silently.

FED_FEEDS = (
    ("speech", "https://www.federalreserve.gov/feeds/speeches.xml"),
    ("testimony", "https://www.federalreserve.gov/feeds/testimony.xml"),
    ("FOMC", "https://www.federalreserve.gov/feeds/press_monetary.xml"),
)

# Surnames to track by name. The monetary-policy feed is included wholesale
# regardless, because an FOMC statement has no speaker and matters anyway.
FED_WATCH = ("Warsh",)


def _rss_items(raw: bytes):
    """(title, url, published) per item. Raises on a feed that is not XML."""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime

    # A UTF-8 BOM ahead of the declaration makes ElementTree reject the whole
    # document. The Fed serves one.
    root = ET.fromstring(raw.lstrip(b"\xef\xbb\xbf"))
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        when = None
        raw_date = (item.findtext("pubDate") or "").strip()
        if raw_date:
            try:
                when = parsedate_to_datetime(raw_date)
            except (TypeError, ValueError):
                when = None
        out.append((" ".join(title.split()),
                    (item.findtext("link") or "").strip() or None,
                    when))
    return out


def fed_officials(today: date, lookback_days: int = 21,
                  watch=FED_WATCH) -> dict:
    """Recent remarks and monetary-policy releases from the Fed's own feeds."""
    cutoff = today - timedelta(days=lookback_days)
    items, notes = [], []
    for kind, url in FED_FEEDS:
        try:
            raw = _get(url).content
            parsed = _rss_items(raw)
        except Exception as exc:  # noqa: BLE001 - one feed, not the section
            notes.append(f"{kind}: {_reason(exc)}")
            continue
        for title, link, when in parsed:
            if when is None or when.date() < cutoff:
                continue
            speaker, _, subject = title.partition(", ")
            if kind == "FOMC":
                # No speaker on a committee release, and all of them count.
                speaker, subject = "FOMC", title
            elif not any(w.lower() == speaker.lower() for w in watch):
                continue
            items.append({
                "date": when.date(),
                "kind": kind,
                "speaker": speaker,
                "title": subject or title,
                "url": link,
            })

    if notes and not items:
        raise RuntimeError("; ".join(notes))

    items.sort(key=lambda i: i["date"], reverse=True)
    return {"items": items, "watching": list(watch),
            "lookback_days": lookback_days,
            "partial": "; ".join(notes) or None,
            "source": "Federal Reserve RSS"}


# --------------------------------------------------- policy desk: operations

FISCAL_BUYBACKS = ("https://api.fiscaldata.treasury.gov/services/api"
                   "/fiscal_service/v1/accounting/od/buybacks_operations")
TD_UPCOMING = "https://www.treasurydirect.gov/TA_WS/securities/upcoming"
# The preliminary announcement, by year and filename. Only needed when the
# operations table has not yet filled in the cap - the table is the primary
# source and this is the belt-and-braces path.
TD_PREANRE = ("https://www.treasurydirect.gov/instit/annceresult/press"
              "/preanre/{year}/{name}")

# Bills are rolled weekly and tell a macro reader nothing. Coupons are where
# duration supply actually lands.
COUPON_TYPES = ("Note", "Bond", "TIPS", "FRN")

# An announced operation this many times the recent norm for ITS OWN maturity
# bucket is a policy signal, not a routine roll. Treasury tripling the long-end
# cap on 9 Sep 2026 is the case this exists for.
#
# The bucket qualifier is load-bearing and was learned the hard way: comparing
# the $6bn long-end announcement against a median that also contained $12.5bn
# short-end liquidity operations produced "1.5x the recent norm of $4.0bn",
# which is arithmetically true of a meaningless population and understates a
# tripling. Buybacks in different maturity buckets are different programmes
# and their sizes are not comparable.
STEP_UP_MULTIPLE = 1.5


def _fd_val(v):
    """Fiscal Data returns the STRING "null" for a missing value, not JSON null.

    Anything comparing that to None sees a truthy string and carries on, which
    is how an announced operation reached a brief as "— accepted of — offered".
    """
    if v is None:
        return None
    t = str(v).strip()
    return None if t in ("", "null", "None") else t


def _fd_amt(v):
    t = _fd_val(v)
    if t is None:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _td_date(raw):
    """TreasuryDirect stamps '2026-09-10T00:00:00'. Date part only."""
    t = _fd_val(raw)
    if t is None:
        return None
    try:
        return date.fromisoformat(t[:10])
    except ValueError:
        return None


def _et_to_lisbon(day: date, clock: str):
    """'01:40 PM' on an operation date -> an aware Lisbon datetime.

    The field is labelled EST year-round but carries local Eastern time, so the
    zone does the DST work rather than a fixed offset.
    """
    t = _fd_val(clock)
    if t is None:
        return None
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            parsed = datetime.strptime(t, fmt).time()
        except ValueError:
            continue
        et = datetime.combine(day, parsed,
                              tzinfo=ZoneInfo("America/New_York"))
        return et.astimezone(LISBON)
    return None


def _buyback_cap_from_xml(row) -> float | None:
    """Announced cap out of the preliminary announcement XML.

    Fallback only. `max_par_amt_redeemed` in the operations table normally
    carries it; this exists because the cap is the whole point of the line and
    losing it to one null field would repeat the 10 Sep miss.
    """
    import xml.etree.ElementTree as ET

    name = _fd_val(row.get("preliminary_ann_xml"))
    day = _td_date(row.get("operation_date"))
    if not name or day is None:
        return None
    try:
        raw = _get(TD_PREANRE.format(year=day.year, name=name), tries=2).content
        root = ET.fromstring(raw.lstrip(b"\xef\xbb\xbf"))
    except Exception:  # noqa: BLE001 - one document, not the section
        return None
    txt = (root.findtext("maxParAmountRedeemed") or "").strip()
    try:
        return float(txt)
    except ValueError:
        return None


def treasury_ops(today: date, buyback_limit: int = 14,
                 auction_limit: int = 4) -> dict:
    """Bond buyback operations and the upcoming coupon auction calendar.

    Operations are split into ANNOUNCED (published, not yet executed) and
    COMPLETED, because they are different news. An announced one carries a cap
    and a time and is the thing to position around; a completed one carries a
    result.

    Correcting an earlier claim in this module's history: the dataset DOES
    carry announced operations. A probe on 6 Sep filtered for operations dated
    today-or-later, got a single row, and concluded the set holds results only.
    It got one row because nothing further had been announced yet. On 10 Sep
    Treasury's $6bn long-end operation was sitting in the table, and the brief
    printed it as "— accepted of — offered" because the cap was never
    requested and "null" arrives as a string.
    """
    announced, completed, auctions, notes = [], [], [], []

    try:
        data = _json(FISCAL_BUYBACKS, params={
            "sort": "-operation_date",
            "page[size]": buyback_limit,
            "fields": ("operation_date,settlement_date,security_type,"
                       "maturity_bucket,total_par_amt_offered,"
                       "total_par_amt_accepted,nbr_issues_accepted,"
                       "max_par_amt_redeemed,nbr_issues_eligible,"
                       "operation_start_time_est,operation_close_time_est,"
                       "preliminary_ann_xml,final_ann_xml"),
        })
        for row in (data.get("data") or []):
            when = _td_date(row.get("operation_date"))
            if when is None:
                continue
            entry = {
                "date": when,
                "settles": _td_date(row.get("settlement_date")),
                "security_type": _fd_val(row.get("security_type")),
                "bucket": _fd_val(row.get("maturity_bucket")),
                "offered": _fd_amt(row.get("total_par_amt_offered")),
                "accepted": _fd_amt(row.get("total_par_amt_accepted")),
                "cap": _fd_amt(row.get("max_par_amt_redeemed")),
                "eligible": _fd_val(row.get("nbr_issues_eligible")),
                "opens": _et_to_lisbon(when,
                                       row.get("operation_start_time_est")),
                "closes": _et_to_lisbon(when,
                                        row.get("operation_close_time_est")),
            }
            # A final announcement is what makes an operation history. Absent
            # it, the operation is still ahead however its date reads.
            if _fd_val(row.get("final_ann_xml")) is None:
                if entry["cap"] is None:
                    entry["cap"] = _buyback_cap_from_xml(row)
                announced.append(entry)
            else:
                completed.append(entry)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"buybacks: {_reason(exc)}")

    # Is an announced cap a step up? Compared only against completed operations
    # in the SAME maturity bucket, and only when there are enough of them to
    # call anything a norm. Median rather than mean, so one earlier outlier
    # cannot hide the next one. No same-bucket history means no claim at all -
    # silence beats a comparison across two different programmes.
    for a in announced:
        peers = sorted(c["cap"] for c in completed
                       if c.get("cap") and c.get("bucket") == a.get("bucket"))
        norm = peers[len(peers) // 2] if len(peers) >= 2 else None
        a["norm"] = norm
        a["norm_n"] = len(peers)
        a["step_up"] = bool(
            norm and a.get("cap") and a["cap"] >= norm * STEP_UP_MULTIPLE)

    try:
        rows = _json(TD_UPCOMING, params={"format": "json"})
        seen = set()
        for row in rows if isinstance(rows, list) else []:
            if (row.get("securityType") or "") not in COUPON_TYPES:
                continue
            when = _td_date(row.get("auctionDate"))
            if when is None or when < today:
                continue
            key = (when, row.get("securityTerm"), row.get("securityType"))
            if key in seen:
                continue
            seen.add(key)
            auctions.append({
                "date": when,
                "term": row.get("securityTerm") or "?",
                "security_type": row.get("securityType"),
                "reopening": str(row.get("reopening") or "").lower() == "yes",
            })
        auctions.sort(key=lambda a: (a["date"], a["term"]))
        auctions = auctions[:auction_limit]
    except Exception as exc:  # noqa: BLE001
        notes.append(f"auctions: {_reason(exc)}")

    if notes and not announced and not completed and not auctions:
        raise RuntimeError("; ".join(notes))

    return {"announced": announced, "completed": completed,
            "auctions": auctions,
            "partial": "; ".join(notes) or None,
            "source": "Treasury Fiscal Data + TreasuryDirect"}


# ------------------------------------------------------------- the fed path

# Three things, three sources, all keyless and all probed from a runner:
#   - the inflation prints, from BLS's public API (v1 takes no key at all)
#   - the policy rate itself, from the desk that sets it
#   - what the market has priced for the next decision
#
# The last one closes an item open since day one. It was recorded as having no
# free source because CME's FedWatch page is a QuikStrike iframe carrying no
# data - true, and still true: CME's own quote service answers datacenter IPs
# with "This IP address is blocked due to suspected web scraping activity".
# That was never a reason the ODDS were unavailable, only that CME's rendering
# of them was. Kalshi lists the same decision as regulated binary contracts
# over a free read API.

BLS_SERIES = "https://api.bls.gov/publicAPI/v1/timeseries/data/{sid}"
NYFED_RATES = "https://markets.newyorkfed.org/api/rates/all/latest.json"
KALSHI_MARKETS = "https://api.elections.kalshi.com/trade-api/v2/markets"
KALSHI_FED_SERIES = "KXFEDDECISION"

# Seasonally adjusted, because month-over-month on an unadjusted index is
# mostly the season.
INFLATION_SERIES = (
    ("CPI", "CUSR0000SA0"),
    ("Core CPI", "CUSR0000SA0L1E"),
    ("PPI final demand", "WPSFD4"),
)

_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")


def _bls_points(series):
    """[(year, month_number, value, footnote_codes)] newest first.

    A value of "-" is a real thing BLS returns - October 2025 CPI carries
    'Data unavailable due to the 2025 lapse in appropriations'. It must not
    become a number.
    """
    out = []
    for row in series.get("data") or []:
        raw = (row.get("value") or "").strip()
        period = (row.get("period") or "")
        if not period.startswith("M") or period == "M13":
            continue        # M13 is an annual average, not a month
        try:
            month = int(period[1:])
            year = int(row.get("year"))
        except (TypeError, ValueError):
            continue
        try:
            value = float(raw)
        except ValueError:
            value = None    # "-" and anything else non-numeric
        codes = [f.get("code") for f in (row.get("footnotes") or [])
                 if isinstance(f, dict) and f.get("code")]
        out.append((year, month, value, codes))
    out.sort(key=lambda p: (p[0], p[1]), reverse=True)
    return out


def inflation() -> dict:
    """Latest CPI, core CPI and PPI prints, with month-over-month and
    year-over-year computed from the index.

    The keyless BLS tier returns no calculations, so both changes are worked
    out here from the raw index values. A print stays in the brief until BLS
    publishes the next one, which is the behaviour Kabil asked for - these are
    monthly releases and the last one remains the current read until superseded.
    """
    prints, notes = [], []
    for label, sid in INFLATION_SERIES:
        try:
            data = _json(BLS_SERIES.format(sid=sid))
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{label}: {_reason(exc)}")
            continue
        if (data.get("status") or "") != "REQUEST_SUCCEEDED":
            msg = "; ".join(str(m) for m in (data.get("message") or [])) or "?"
            notes.append(f"{label}: BLS said {msg[:60]}")
            continue
        series = (data.get("Results", {}).get("series") or [{}])[0]
        pts = _bls_points(series)
        cur = next((p for p in pts if p[2] is not None), None)
        if cur is None:
            notes.append(f"{label}: no usable observation")
            continue
        year, month, value, codes = cur

        def _find(y, m):
            return next((p[2] for p in pts if p[0] == y and p[1] == m), None)

        prev = _find(year, month - 1) if month > 1 else _find(year - 1, 12)
        yago = _find(year - 1, month)
        prints.append({
            "label": label,
            "period": f"{_MONTHS[month - 1]} {year}",
            "year": year,
            "month": month,
            "index": value,
            "mom": (value / prev - 1) * 100 if prev else None,
            "yoy": (value / yago - 1) * 100 if yago else None,
            "preliminary": "P" in codes,
            "series_id": sid,
        })

    if notes and not prints:
        raise RuntimeError("; ".join(notes))
    return {"prints": prints, "partial": "; ".join(notes) or None,
            "source": "BLS public API"}


def policy_rate() -> dict:
    """The current target range and where the effective rate is sitting in it.

    Straight from the New York Fed's own rates endpoint, which is the desk
    that publishes the effective rate, so this is the decision itself rather
    than a report of it.
    """
    rows = _json(NYFED_RATES).get("refRates") or []
    effr = next((r for r in rows if (r.get("type") or "").upper() == "EFFR"),
                None)
    if not effr:
        raise RuntimeError("EFFR not in the New York Fed response")
    return {
        "as_of": _td_date(effr.get("effectiveDate")),
        "effr": effr.get("percentRate"),
        "target_low": effr.get("targetRateFrom"),
        "target_high": effr.get("targetRateTo"),
        "volume_bn": effr.get("volumeInBillions"),
        "source": "New York Fed",
    }


def _kalshi_prob(m):
    """Mid of the book as a probability, falling back to the last trade.

    A mid is the honest read when both sides are quoted. With one side missing
    the last trade is all there is, and how stale that might be is the reason
    the spread is reported alongside it.
    """
    def _f(key):
        try:
            return float(m.get(key))
        except (TypeError, ValueError):
            return None

    bid, ask = _f("yes_bid_dollars"), _f("yes_ask_dollars")
    if bid is not None and ask is not None and ask > 0:
        return (bid + ask) / 2, (ask - bid)
    last = _f("last_price_dollars")
    return (last, None) if last is not None else (None, None)


def fed_odds(today: date) -> dict:
    """What the market has priced for the next FOMC decision.

    Kalshi rather than CME: the contracts are structured per meeting with
    machine-readable strikes, the read API needs no key, and CME blocks
    datacenter IPs outright. These are prediction-market prices, not
    futures-implied probabilities, and the brief says so - they are a
    different instrument and can disagree.
    """
    data = _json(KALSHI_MARKETS, params={
        "series_ticker": KALSHI_FED_SERIES,
        "status": "open",
        "limit": 200,
    })
    markets = data.get("markets") or []
    if not markets:
        raise RuntimeError("Kalshi returned no open Fed decision contracts")

    # Group by meeting, then take the meeting that settles soonest.
    by_event: dict[str, list] = {}
    for m in markets:
        by_event.setdefault(m.get("event_ticker") or "?", []).append(m)

    def _closes(group):
        stamps = []
        for m in group:
            raw = (m.get("close_time") or "").replace("Z", "+00:00")
            try:
                stamps.append(datetime.fromisoformat(raw))
            except ValueError:
                continue
        return min(stamps) if stamps else None

    dated = [(ev, g, _closes(g)) for ev, g in by_event.items()]
    dated = [d for d in dated if d[2] and d[2].date() >= today]
    if not dated:
        raise RuntimeError("no Fed decision contract settles in the future")
    event, group, closes = min(dated, key=lambda d: d[2])

    outcomes = []
    for m in group:
        prob, spread = _kalshi_prob(m)
        if prob is None:
            continue
        try:
            volume = float(m.get("volume_fp"))
        except (TypeError, ValueError):
            volume = None
        outcomes.append({
            "label": (m.get("yes_sub_title") or m.get("subtitle")
                      or m.get("ticker") or "?"),
            "prob": prob * 100.0,
            "spread": spread * 100.0 if spread is not None else None,
            "volume": volume,
            "ticker": m.get("ticker"),
        })
    if not outcomes:
        raise RuntimeError("Fed contracts carried no usable prices")

    # Mutually exclusive by construction, so the mids should sum near 100.
    # They will not sum exactly, and normalising silently would hide a book
    # too wide to be worth quoting - so the raw total is reported.
    total = sum(o["prob"] for o in outcomes)
    outcomes.sort(key=lambda o: o["prob"], reverse=True)
    return {
        "event": event,
        "closes": closes.astimezone(LISBON) if closes else None,
        "outcomes": outcomes,
        "raw_total": total,
        "source": "Kalshi (prediction market, mid of book)",
    }


# ------------------------------------------------------------------ backdrop

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# Round 16 settled the method and it is a rule, not a preference: ask with an
# EXPLICIT realtime window. FRED's default window wanders between calls -
# round 15 saw two requests seconds apart disagree about what "today" was -
# and a wandering vintage is how a revised figure gets printed as a first
# print. Never use `releases/dates` to decide publication either; it lists
# SCHEDULED dates, which is not the same claim. See PROJECT_STATE §12.10.
BACKDROP_SERIES = (
    # id, label, unit, how many observations we need
    ("UNRATE", "Unemployment", "%", 13),
    ("T10Y2Y", "10Y–2Y spread", "pp", 30),
    ("CPIAUCSL", "CPI", "index", 14),
)


def _fred_obs(series_id: str, key: str, limit: int, today: date):
    """Latest observations for a series, on today's vintage explicitly."""
    data = _json(FRED_BASE, params={
        "series_id": series_id,
        "api_key": key,
        "file_type": "json",
        "limit": limit,
        "sort_order": "desc",
        # The whole of §12.10 in two parameters.
        "realtime_start": today.isoformat(),
        "realtime_end": today.isoformat(),
    })
    out = []
    for row in data.get("observations") or []:
        raw = row.get("value")
        if raw in (None, "", "."):        # FRED writes "." for a missing point
            continue
        try:
            out.append((date.fromisoformat(row["date"]), float(raw)))
        except (ValueError, KeyError, TypeError):
            continue
    return out


def backdrop(today: date | None = None) -> dict:
    """The economic backdrop: labour, the curve, and the trend in prices.

    This is the FRED work repurposed. It was probed across rounds 14-16 to
    answer *"what did CPI come in at this morning"* for a second edition that
    was then cancelled - Kabil is at the desk when data prints, so a brief
    reporting the number afterwards tells him what is already on his screens.
    The method survives; the question changed. These are slow-moving series
    that frame everything else, and a brief is the right place for them
    precisely because they do not move.

    **Every line carries its observation date.** Two of the three are monthly
    and one is daily-with-a-lag, so a number printed without an age reads as
    today's - which is the present-but-misleading failure (§3.9), not a
    missing-data one.
    """
    key = (os.environ.get("FRED_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("FRED_API_KEY is not set")
    today = today or datetime.now(LISBON).date()

    out, notes = [], []
    for sid, label, unit, limit in BACKDROP_SERIES:
        try:
            obs = _fred_obs(sid, key, limit, today)
        except Exception as exc:  # noqa: BLE001 - one series, not the section
            notes.append(f"{label}: {_reason(exc)}")
            continue
        if not obs:
            notes.append(f"{label}: no observations")
            continue
        when, value = obs[0]
        entry = {"id": sid, "label": label, "unit": unit,
                 "as_of": when, "value": value, "prior": None,
                 "yoy": None, "ann_3m": None}
        if len(obs) > 1:
            entry["prior"] = obs[1][1]
        if sid == "CPIAUCSL":
            # The index itself means nothing to a reader. Two cuts do: the
            # year-over-year rate, and the 3-month annualised, which turns
            # faster and is the one that shows a trend changing. Neither
            # duplicates EXPECTATIONS, which carries the latest month-on-month
            # print from BLS.
            by_date = dict(obs)
            def _idx(months_back):
                for d_, v_ in obs:
                    if (when.year - d_.year) * 12 + (when.month - d_.month) == months_back:
                        return v_
                return None
            year_ago, three_ago = _idx(12), _idx(3)
            if year_ago:
                entry["yoy"] = (value / year_ago - 1) * 100
            if three_ago:
                entry["ann_3m"] = ((value / three_ago) ** 4 - 1) * 100
        out.append(entry)

    if not out:
        raise RuntimeError("; ".join(notes) or "no series returned")
    return {"series": out, "partial": "; ".join(notes) or None,
            "source": "FRED (St. Louis Fed)"}


# ---------------------------------------------------------------------- news

# Round 14 probed the four accounts Kabil named at their primary sources and
# the result inverted the premise: CNBC, which he did not name, beat three of
# the four. WatcherGuru answered 200 with perfectly formed items whose newest
# was 41.9 hours old; @DeItaone relays a Bloomberg terminal and has no free
# primary by design. See §12.8.
NEWS_FEEDS = (
    # label, url, kind. `kind` decides how the brief typesets it, and the
    # distinction is load-bearing: D16 admits ZeroHedge as commentary on the
    # condition that it is visibly marked as such. In a brief where every line
    # is a fetched number with a source and an age stamp, an opinion headline
    # renders with identical authority - §3.9 inverted.
    ("CNBC", "https://search.cnbc.com/rs/search/combinedcms/view.xml"
             "?partnerId=wrss01&id=100003114", "wire"),
    ("ZeroHedge", "https://feeds.feedburner.com/zerohedge/feed", "commentary"),
)

# How far back to look. The brief builds at 09:20 Lisbon, so this has to cover
# the whole US session and the Asian one after it. ZeroHedge's window was
# measured at only 21.6h in round 14, so asking for more than that would
# silently return less from one source than the other.
NEWS_WINDOW_HOURS = 18
NEWS_PER_SOURCE = 4


def news(now: datetime | None = None) -> dict:
    """Recent headlines, each tagged with where it came from and how old.

    Nothing here is a number, which makes it the only section in the brief
    that is not a fetched figure. That is exactly why every item carries its
    source and its age, and why commentary is marked apart from a wire.
    """
    now = now or datetime.now(LISBON)
    cutoff = now - timedelta(hours=NEWS_WINDOW_HOURS)
    items, notes = [], []
    for label, url, kind in NEWS_FEEDS:
        try:
            parsed = _rss_items(_get(url).content)
        except Exception as exc:  # noqa: BLE001 - one feed, not the section
            notes.append(f"{label}: {_reason(exc)}")
            continue
        fresh = []
        for title, link, when in parsed:
            if when is None:
                # An undated headline cannot be placed in a window, and
                # "recent" is the whole claim this section makes.
                continue
            when = when.astimezone(LISBON)
            if when < cutoff:
                continue
            fresh.append({"title": title, "url": link, "when": when,
                          "source": label, "kind": kind})
        if not fresh:
            notes.append(f"{label}: nothing in the last {NEWS_WINDOW_HOURS}h")
        fresh.sort(key=lambda i: i["when"], reverse=True)
        items.extend(fresh[:NEWS_PER_SOURCE])

    if not items and notes:
        raise RuntimeError("; ".join(notes))
    items.sort(key=lambda i: i["when"], reverse=True)
    return {"items": items, "window_hours": NEWS_WINDOW_HOURS,
            "partial": "; ".join(notes) or None,
            "source": "CNBC + ZeroHedge"}


# ----------------------------------------------------------- liquidations

OKX_LIQ = "https://www.okx.com/api/v5/public/liquidation-orders"

# Round 18 overturned a verdict this project carried from rev 1: the register
# said `S2 - CoinGlass, no free tier, $29/mo`, and §12.4a is the section about
# exactly that mistake. CoinGlass being paid is a property of that ROUTE, not
# of the world. OKX answers keyless.
#
# Round 19 then established the shape, and the shape constrains the claim:
#
#   * One page is 100 rows and spans well under an hour - 0.47h when measured.
#     **A 24-hour total would need roughly fifty paged calls**, so the brief
#     says "recent" and means it. Printing "24h liquidations" off one page
#     would be a number measuring something other than its own label, which is
#     the failure this project keeps meeting.
#
#   * `sz` is in CONTRACTS, not coins. ETH-USDT-SWAP is 0.1 ETH a contract, so
#     `sz * bkPx` overstates notional tenfold. The multiplier lives in a
#     different endpoint (`instruments`, field `ctVal`) that nobody has
#     probed, so **this fetcher does not compute notional at all.** Counts and
#     side skew need no multiplier and are printed; dollars wait for a probe.
OKX_BOOKS = (("BTC", "BTC-USDT"), ("ETH", "ETH-USDT"))
LIQ_PAGE = 100


def liquidations(books=OKX_BOOKS) -> dict:
    """Recent forced closes per book, with the side that got hit.

    The four cases a positioning read cares about need price direction beside
    this, and the brief already has that. What this adds is which side was
    forced - and a page of it, not a day.
    """
    out, notes = [], []
    newest = oldest = None
    for label, uly in books:
        try:
            data = _json(OKX_LIQ, params={"instType": "SWAP", "uly": uly,
                                          "state": "filled",
                                          "limit": str(LIQ_PAGE)})
        except Exception as exc:  # noqa: BLE001 - one book, not the section
            notes.append(f"{label}: {_reason(exc)}")
            continue
        rows = []
        for block in data.get("data") or []:
            rows.extend(block.get("details") or [])
        if not rows:
            notes.append(f"{label}: no rows returned")
            continue
        longs = sum(1 for r in rows if r.get("posSide") == "long")
        shorts = sum(1 for r in rows if r.get("posSide") == "short")
        stamps = sorted(int(r["ts"]) for r in rows if r.get("ts"))
        if stamps:
            first = datetime.fromtimestamp(stamps[0] / 1000, timezone.utc)
            last = datetime.fromtimestamp(stamps[-1] / 1000, timezone.utc)
            newest = last if newest is None else max(newest, last)
            oldest = first if oldest is None else min(oldest, first)
        out.append({"label": label, "uly": uly, "rows": len(rows),
                    "longs": longs, "shorts": shorts})

    if not out:
        raise RuntimeError("; ".join(notes) or "no books returned")
    span_h = ((newest - oldest).total_seconds() / 3600
              if newest and oldest else None)
    return {"books": out, "newest": newest, "span_hours": span_h,
            "page_size": LIQ_PAGE, "partial": "; ".join(notes) or None,
            "source": "OKX (single venue)"}


# --------------------------------------------------- IBIT, Brent, CME BTC

# All three passed round 19 with the brief's own headers. They had drawn `429`
# in rounds 17 and 18, and §3.28 recorded that as "Yahoo rate-limits an
# Actions runner" - which was wrong, and wrong because the probe sent a
# browser User-Agent with a JSON Accept while sources.py sends a plain one. A
# browser fingerprint on an API endpoint is an ordinary thing to rate-limit.
def yahoo_extra() -> dict:
    """IBIT, Brent and CME BTC futures - one call shape, three instruments."""
    out, notes = {}, []
    for symbol, label in (("IBIT", "IBIT"), ("BZ=F", "Brent"),
                          ("BTC=F", "CME BTC")):
        try:
            out[label] = _yahoo_quote(symbol)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{label}: {_reason(exc)}")
    if not out:
        raise RuntimeError("; ".join(notes))
    return {"quotes": out, "partial": "; ".join(notes) or None,
            "source": "Yahoo chart API"}


# ------------------------------------------------- liquidity plumbing (FRED)

# Addendum B. BACKDROP as first specified carries the economic PICTURE;
# these three carry the MECHANISM - the plumbing policy actually reaches risk
# assets through. Same host, same method, same key, so no new probe.
#
# ⚠ Deliberately NOT computed: a "net liquidity" composite. The common
# construct (balance sheet minus TGA minus RRP) has modelling choices baked
# into it and different desks compute it differently. Printed as one headline
# number in the same typeface as fetched data, it would be a derived opinion
# wearing a fetched number's clothes - §3.9 inverted, which is the one thing
# this brief has never done. The three components print with their own dates.
PLUMBING_SERIES = (
    ("RRPONTSYD", "Reverse repo", "$bn", 10),
    ("WTREGEN", "Treasury account", "$bn", 6),
    ("WRESBAL", "Bank reserves", "$bn", 6),
)


def plumbing(today: date | None = None) -> dict:
    """Overnight RRP, the Treasury General Account, and reserve balances."""
    key = (os.environ.get("FRED_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("FRED_API_KEY is not set")
    today = today or datetime.now(LISBON).date()
    out, notes = [], []
    for sid, label, unit, limit in PLUMBING_SERIES:
        try:
            obs = _fred_obs(sid, key, limit, today)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"{label}: {_reason(exc)}")
            continue
        if not obs:
            notes.append(f"{label}: no observations")
            continue
        when, value = obs[0]
        prior = obs[1][1] if len(obs) > 1 else None
        out.append({"id": sid, "label": label, "unit": unit, "as_of": when,
                    "value": value, "prior": prior})
    if not out:
        raise RuntimeError("; ".join(notes) or "no series returned")
    return {"series": out, "partial": "; ".join(notes) or None,
            "source": "FRED (St. Louis Fed)"}
