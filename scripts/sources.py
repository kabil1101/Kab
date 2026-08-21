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

import re
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests

LISBON = ZoneInfo("Europe/Lisbon")
UTC = timezone.utc

FF_THIS_WEEK = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FF_NEXT_WEEK = "https://nfs.faireconomy.media/ff_calendar_nextweek.json"
KRAKEN_TICKER = "https://api.kraken.com/0/public/Ticker?pair=XBTUSD,ETHUSD,SOLUSD"
FNG = "https://api.alternative.me/fng/?limit=8"
FARSIDE_BTC = "https://farside.co.uk/btc/"
FARSIDE_ETH = "https://farside.co.uk/eth/"
DERIBIT_BOOK = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"
COINGECKO_GLOBAL = "https://api.coingecko.com/api/v3/global"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

UA = "Mozilla/5.0 (compatible; market-brief/1.0; +https://github.com/kabil1101/Kab)"
HEADERS = {"User-Agent": UA, "Accept": "*/*"}
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
    return type(exc).__name__


def _get(url: str, *, params=None, tries: int = 3):
    """GET with bounded retries. Raises a compact error on final failure."""
    last = None
    for _ in range(tries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
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
    seen: set = set()
    events = _parse_ff(_json(FF_THIS_WEEK), seen)
    today = datetime.now(LISBON).date()
    if today.weekday() >= 2:  # Wed or later
        try:
            events += _parse_ff(_json(FF_NEXT_WEEK), seen)
        except Exception:
            pass  # forward view degrades, today's view still stands
    events.sort(key=lambda e: e["dt_lis"])
    return {"events": events, "source": "ForexFactory (nfs.faireconomy.media)"}


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

_NUM = re.compile(r"^\(?-?[\d,]+\.?\d*\)?$")


def _money(cell: str):
    """Farside prints negatives in parentheses."""
    c = cell.strip().replace(",", "")
    if c in ("", "-", "–"):
        return None
    neg = c.startswith("(") and c.endswith(")")
    c = c.strip("()")
    try:
        v = float(c)
    except ValueError:
        return None
    return -v if neg else v


def _farside(url: str):
    from bs4 import BeautifulSoup

    html = _get(url).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("no table found")

    rows = []
    header = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if not cells:
            continue
        if not header and any(c.upper() in ("IBIT", "FBTC", "ETHA") for c in cells):
            header = [c.strip() for c in cells]
            continue
        # A data row starts with a parseable date.
        try:
            d = datetime.strptime(cells[0], "%d %b %Y").date()
        except ValueError:
            continue
        rows.append({"date": d, "cells": cells})

    if not rows:
        raise RuntimeError("no data rows parsed")
    rows.sort(key=lambda r: r["date"])

    def col(row, name):
        if not header:
            return None
        try:
            i = [h.upper() for h in header].index(name.upper())
        except ValueError:
            return None
        return _money(row["cells"][i]) if i < len(row["cells"]) else None

    def total(row):
        v = col(row, "Total")
        if v is None:                      # fall back to the last numeric cell
            for c in reversed(row["cells"][1:]):
                v = _money(c)
                if v is not None:
                    break
        return v

    recent = rows[-6:]
    return {
        "header": header,
        "latest_date": rows[-1]["date"],
        "latest_total": total(rows[-1]),
        "recent": [
            {"date": r["date"], "total": total(r),
             "ibit": col(r, "IBIT"), "fbtc": col(r, "FBTC"),
             "etha": col(r, "ETHA")}
            for r in recent
        ],
        "source": "Farside Investors",
    }


def etf_flows_btc():
    return _farside(FARSIDE_BTC)


def etf_flows_eth():
    return _farside(FARSIDE_ETH)


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
