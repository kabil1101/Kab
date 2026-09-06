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
        return {
            "expiry": exp,
            "max_pain": _max_pain(by_strike),
            "top_call_strike": top_call,
            "top_call_oi": calls.get(top_call),
            "top_put_strike": top_put,
            "top_put_oi": puts.get(top_put),
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
    d = _json(COINGECKO_GLOBAL)["data"]
    return {
        "total_mcap_usd": d["total_market_cap"]["usd"],
        "mcap_change_24h_pct": d.get("market_cap_change_percentage_24h_usd"),
        "btc_dominance": d["market_cap_percentage"].get("btc"),
        "eth_dominance": d["market_cap_percentage"].get("eth"),
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

# Bills are rolled weekly and tell a macro reader nothing. Coupons are where
# duration supply actually lands.
COUPON_TYPES = ("Note", "Bond", "TIPS", "FRN")


def _td_date(raw):
    """TreasuryDirect stamps '2026-09-10T00:00:00'. Date part only."""
    if not raw:
        return None
    try:
        return date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def treasury_ops(today: date, buyback_limit: int = 4,
                 auction_limit: int = 4) -> dict:
    """Bond buyback operations and the upcoming coupon auction calendar.

    Note what is NOT here: a forward buyback schedule. The Fiscal Data set was
    queried for operations dated on or after today and returned only the one
    that had already run, so it carries results and not announcements. The
    brief therefore reports the last operation and its size, and does not
    pretend to know the next one.
    """
    buybacks, auctions, notes = [], [], []

    try:
        data = _json(FISCAL_BUYBACKS, params={
            "sort": "-operation_date",
            "page[size]": buyback_limit,
            "fields": ("operation_date,settlement_date,security_type,"
                       "maturity_bucket,total_par_amt_offered,"
                       "total_par_amt_accepted,nbr_issues_accepted"),
        })
        for row in (data.get("data") or []):
            when = _td_date(row.get("operation_date"))
            if when is None:
                continue

            def _amt(key):
                try:
                    return float(row.get(key))
                except (TypeError, ValueError):
                    return None

            buybacks.append({
                "date": when,
                "settles": _td_date(row.get("settlement_date")),
                "security_type": row.get("security_type") or None,
                "bucket": row.get("maturity_bucket") or None,
                "offered": _amt("total_par_amt_offered"),
                "accepted": _amt("total_par_amt_accepted"),
            })
    except Exception as exc:  # noqa: BLE001
        notes.append(f"buybacks: {_reason(exc)}")

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

    if notes and not buybacks and not auctions:
        raise RuntimeError("; ".join(notes))

    return {"buybacks": buybacks, "auctions": auctions,
            "partial": "; ".join(notes) or None,
            "source": "Treasury Fiscal Data + TreasuryDirect"}
