"""Brief rendering: markdown for logs, HTML for the email body.

Formatting rules that matter:
  - Every printed time is Lisbon local, labelled LIS.
  - A step that could not be sourced prints "unavailable" with the reason.
    That is a correct outcome, not a failure to paper over.
  - No estimated or remembered figures ever reach this layer; the renderer
    can only print what a fetcher actually returned.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import state
import watchlist

LISBON = ZoneInfo("Europe/Lisbon")
UTC = timezone.utc

LOW_IMPACT_KEEP = ("inventories", "crude oil", "natural gas", "speaks",
                   "bond auction", "auction")


def _hhmm(dt):
    return dt.strftime("%H:%M")


def _dash(v):
    return v if v else "—"


def _keep_low(title: str) -> bool:
    t = title.lower()
    return any(k in t for k in LOW_IMPACT_KEEP)


def _is_cb_speaker(title: str) -> bool:
    t = title.lower()
    return "speaks" in t or "press conference" in t or "testimony" in t


def select_today(events, today):
    out = []
    for e in events:
        if e["dt_lis"].date() != today:
            continue
        imp = e["impact"].lower()
        if imp in ("high", "medium") or (imp == "low" and _keep_low(e["title"])):
            out.append(e)
        elif imp == "holiday":
            out.append(e)
    return out


def select_forward(events, today, sessions=5):
    """Next N trading days of High-impact events."""
    days, cursor = [], today
    while len(days) < sessions:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            days.append(cursor)
    wanted = set(days)
    return [e for e in events
            if e["dt_lis"].date() in wanted and e["impact"].lower() == "high"]


def _as_of_stamp(as_of, now):
    """Timestamp a quote, and never show a bare time for a stale one.

    A time with no date reads as current. Friday's close rendered as
    "(as of 21:59 LIS)" is character-for-character what a live quote looks
    like, so on a Monday the reader has no way to tell it is three days old.
    Anything not from today carries its date and its age in words.
    """
    if not as_of:
        return ""
    if as_of.date() == now.date():
        return f" (as of {_hhmm(as_of)} LIS)"
    age = now - as_of
    hours = int(age.total_seconds() // 3600)
    age_txt = f"{hours}h old" if hours < 48 else f"{age.days}d old"
    return f" (as of {as_of:%a %d %b} {_hhmm(as_of)} LIS — {age_txt})"


def _range_pos(pair):
    """Where the last price sits in the 24h range, 0 = low, 100 = high."""
    lo, hi = pair.get("low_24h"), pair.get("high_24h")
    if lo is None or hi is None or hi <= lo:
        return None
    return (pair["last"] - lo) / (hi - lo) * 100.0


def subject(ctx) -> str:
    """Subject line that says whether the brief is worth opening.

    The inbox list previously showed only a date, which carries no signal at
    all. Everything here comes from data already fetched; nothing new is
    requested for it. The `Market Brief - ` prefix is load-bearing - the
    chat-side Mode Check matches on it - so it stays exactly as it was.
    """
    now = ctx["now"]
    parts = [f"Market Brief - {now:%-d %b}"]

    c = ctx.get("crypto")
    if c and c["ok"]:
        btc = next((p for p in c["data"]["pairs"] if p["symbol"] == "BTC"), None)
        if btc:
            parts.append(f"BTC {btc['last'] / 1000:.1f}k "
                         f"{btc['pct_since_utc_midnight']:+.1f}%")

    cal = ctx.get("calendar")
    if cal and cal["ok"]:
        todays = select_today(cal["data"]["events"], now.date())
        top = [e for e in todays
               if e["impact"].lower() == "high" and e["country"] == "USD"]
        ahead = [e for e in top if e["dt_lis"] > now]
        pick = ahead[0] if ahead else (top[0] if top else None)
        if pick:
            title = pick["title"]
            if len(title) > 28:
                title = title[:27] + "\u2026"
            parts.append(f"{title} {_hhmm(pick['dt_lis'])}")

    # A policy date inside a week is the one thing worth seeing without
    # opening the mail, because it is the only item here that needs acting on
    # before the day it lands. Further out it is not news yet and would just
    # crowd the line.
    upcoming = radar_events(ctx, now.date())
    if upcoming:
        days = (upcoming[0]["date"] - now.date()).days
        if days <= 7:
            label = upcoming[0]["title"]
            if len(label) > 30:
                label = label[:29].rstrip() + "\u2026"
            parts.append(f"{_tminus(days)} {label}")

    return " \u00b7 ".join(parts)


def _money(v, unit="$"):
    if v is None:
        return "—"
    sign = "-" if v < 0 else "+"
    return f"{sign}{unit}{abs(v):,.1f}m"


def build(ctx) -> tuple[str, str]:
    """Return (markdown, html)."""
    md, html = [], []
    now = ctx["now"]
    today = now.date()

    title = f"MARKET BRIEF — {now.strftime('%A, %d %B %Y')}"
    md.append(f"# {title}\n")
    md.append(f"*Cloud run — built {_hhmm(now)} LIS.*\n")
    html.append(_h_open(title, f"Cloud run — built {_hhmm(now)} LIS."))

    # ---- THE SETUP -----------------------------------------------------
    setup = _setup_bullets(ctx)
    md.append("## THE SETUP\n")
    for b in setup:
        md.append(f"- {b}")
    md.append("")
    html.append(_h_section("The Setup"))
    html.append("<ul>" + "".join(f"<li>{_hb(b)}</li>" for b in setup) + "</ul>")

    # ---- CALENDAR ------------------------------------------------------
    md.append("## CALENDAR\n")
    html.append(_h_section("Calendar"))
    cal = ctx["calendar"]
    if not cal["ok"]:
        line = f"Calendar unavailable — {cal['error']}"
        md.append(line + "\n")
        html.append(f"<p><em>{_hb(line)}</em></p>")
    else:
        todays = select_today(cal["data"]["events"], today)
        if not todays:
            md.append("No High or Medium impact events scheduled today.\n")
            html.append("<p>No High or Medium impact events scheduled today.</p>")
        else:
            md.append("| Time LIS | CCY | Event | F | P | Impact |")
            md.append("|---|---|---|---|---|---|")
            rows = []
            for e in todays:
                bold = e["impact"].lower() == "high" and e["country"] == "USD"
                bold = bold or _is_cb_speaker(e["title"])
                name = f"**{e['title']}**" if bold else e["title"]
                md.append(
                    f"| {_hhmm(e['dt_lis'])} | {e['country']} | {name} | "
                    f"{_dash(e['forecast'])} | {_dash(e['previous'])} | {e['impact']} |"
                )
                rows.append((_hhmm(e["dt_lis"]), e["country"], e["title"],
                             _dash(e["forecast"]), _dash(e["previous"]),
                             e["impact"], bold))
            md.append("")
            html.append(_h_table(
                ["Time LIS", "CCY", "Event", "F", "P", "Impact"], rows))

        fwd = select_forward(cal["data"]["events"], today)
        md.append("**Next 5 sessions — High impact**\n")
        html.append("<p><strong>Next 5 sessions — High impact</strong></p>")
        if fwd:
            items = [f"{e['dt_lis'].strftime('%a %d %b')} {_hhmm(e['dt_lis'])} LIS | "
                     f"{e['country']} | {e['title']}" for e in fwd]
            for i in items:
                md.append(f"- {i}")
            html.append("<ul>" + "".join(f"<li>{_hb(i)}</li>" for i in items) + "</ul>")
        else:
            # Distinguish an empty forward view from a dead feed. Printing
            # "none scheduled" when the fetch failed is the worst outcome:
            # it reads as an all-clear.
            # ForexFactory publishes only the current week, so late in the
            # week the forward view genuinely runs out. Saying that beats an
            # empty section, which reads as "nothing scheduled".
            note = ("No further High-impact events this week. ForexFactory "
                    "publishes only the current week, so next week is not "
                    "covered." if cal["data"].get("week_only")
                    else "None scheduled in the forward feed.")
            md.append(f"- {note}")
            html.append(f"<ul><li>{_hb(note)}</li></ul>")
        md.append("")

    # ---- AHEAD ---------------------------------------------------------
    # Deliberately above CRYPTO: the point of this section is to be seen every
    # morning for weeks before the date, not to be found by scrolling.
    radar = radar_events(ctx, today)
    md.append("## AHEAD — POLICY & GEOPOLITICS\n")
    html.append(_h_section("Ahead — Policy &amp; Geopolitics"))
    pr = ctx.get("policy_radar")
    if radar:
        for name, rows in _radar_groups(radar, today):
            md.append(f"**{name}**\n")
            html.append(f"<p><strong>{_esc(name)}</strong></p>")
            items = []
            for days, e in rows:
                line = _radar_text(days, e)
                md.append(f"- {line}"
                          + (f"  \n  {e['url']}" if e.get("url") else ""))
                link = (f" <a href='{_esc(e['url'])}'>source</a>"
                        if e.get("url") else "")
                items.append(_hb(line) + link)
            html.append("<ul>" + "".join(f"<li>{i}</li>" for i in items)
                        + "</ul>")
            md.append("")
    else:
        # An empty radar is a real state - most weeks nothing new has been
        # signed with a future date - but it must not read as "nothing is
        # coming" when the fetch simply failed.
        if pr and not pr["ok"]:
            note = f"Policy radar unavailable — {pr['error']}"
        else:
            note = (f"Nothing dated in the next {RADAR_HORIZON_DAYS} days from "
                    f"either the Federal Register or the watchlist.")
        md.append(f"- {note}\n")
        html.append(f"<ul><li>{_hb(note)}</li></ul>")

    # Say how much was actually read, so an empty section can be told apart
    # from a section that never looked.
    if pr and pr["ok"]:
        d = pr["data"]
        prov = (f"Scanned {d['texts_scanned']} presidential documents "
                f"(last 90 days) plus rules with a future effective date "
                f"· {d['source']}")
        if d.get("partial"):
            prov += f" · partial: {d['partial']}"
        md.append(f"*{prov}*\n")
        html.append(f"<p class='muted'><em>{_esc(prov)}</em></p>")
    wl_problems = (ctx.get("watchlist") or {}).get("problems") or []
    if wl_problems:
        bad = "watchlist.txt: " + "; ".join(wl_problems[:4])
        md.append(f"*{bad}*\n")
        html.append(f"<p class='muted'><em>{_esc(bad)}</em></p>")

    # ---- CRYPTO --------------------------------------------------------
    md.append("## CRYPTO\n")
    html.append(_h_section("Crypto"))
    c = ctx["crypto"]
    if not c["ok"]:
        md.append(f"Prices unavailable — {c['error']}\n")
        html.append(f"<p><em>Prices unavailable — {c['error']}</em></p>")
    else:
        lines = []
        prev = ctx.get("prev") or {}
        for p in c["data"]["pairs"]:
            d = state.delta(prev, p["symbol"].lower(), p["last"])
            vs = f" · {d[1]:+.1f}% vs yesterday" if d else ""
            lines.append(
                f"**{p['symbol']}** ${p['last']:,.2f}{vs} · "
                f"{p['pct_since_utc_midnight']:+.2f}% since 00:00 UTC · "
                f"24h range ${p['low_24h']:,.2f}–${p['high_24h']:,.2f} · "
                f"24h VWAP ${p['vwap_24h']:,.2f}"
            )
        for l in lines:
            md.append(f"- {l}")
        html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in lines) + "</ul>")
        md.append("")

    for label, key in (("Options positioning", "options_btc"),
                       ("Derivatives", "derivatives")):
        s = ctx.get(key)
        if s is None:
            continue
        if not s["ok"]:
            line = f"**{label}:** unavailable — {s['error']}"
            md.append(line)
            html.append(f"<p>{_hb(line)}</p>")
        else:
            body = _options_line(s["data"]) if key == "options_btc" else s["data"]
            md.append(f"**{label}:** {body}")
            html.append(f"<p><strong>{_esc(label)}:</strong> {_hb(str(body))}</p>")
    md.append("")

    # ---- FLOWS ---------------------------------------------------------
    md.append("## FLOWS\n")
    html.append(_h_section("Flows"))
    fb = ctx["flows_btc"]
    if not fb["ok"]:
        line = f"**BTC ETF:** unavailable — {fb['error']}"
    else:
        d = fb["data"]
        run = [r["total"] for r in d["recent"] if r["total"] is not None]
        line = (f"**BTC ETF** {d['latest_date']:%d %b}: {_money(d['latest_total'])} "
                f"total · {_run_note(run)}")
        ibit, fbtc = d["recent"][-1].get("ibit"), d["recent"][-1].get("fbtc")
        if ibit is not None or fbtc is not None:
            line += f" · IBIT {_money(ibit)} · FBTC {_money(fbtc)}"
        if d.get("updated_through"):
            line += f" · dataset through {d['updated_through']}"
        line += f" · via {d['source']}"
    md.append(f"- {line}")
    html.append(f"<p>{_hb(line)}</p>")
    md.append("")

    # ---- DERIVATIVES ---------------------------------------------------
    md.append("## DERIVATIVES\n")
    html.append(_h_section("Derivatives"))
    dlines = []
    for label, key in (("BTC", "perp_btc"), ("ETH", "perp_eth")):
        p_ = ctx.get(key)
        if p_ is None:
            continue
        if not p_["ok"]:
            dlines.append(f"**{label} perp:** unavailable — {p_['error']}")
            continue
        d = p_["data"]
        f8 = d.get("funding_8h")
        # funding_8h is a rate: 0.0001 is 0.01% per 8h. Flag the levels the
        # brief has always called out.
        if f8 is None:
            fund = "funding —"
        else:
            pct = f8 * 100
            flag = " ⚠" if (pct > 0.05 or pct < 0) else ""
            fund = f"funding {pct:+.4f}%/8h{flag}"
        oi = d.get("open_interest")
        oi_txt = f"OI {oi:,.0f}" if oi is not None else "OI —"
        dlines.append(f"**{label} perp** {fund} · {oi_txt} · {d['source']}")
    for l in dlines:
        md.append(f"- {l}")
    html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in dlines) + "</ul>")
    md.append("")

    # ---- SENTIMENT -----------------------------------------------------
    md.append("## SENTIMENT\n")
    html.append(_h_section("Sentiment"))
    fg = ctx["fear_greed"]
    if not fg["ok"]:
        line = f"Crypto Fear & Greed unavailable — {fg['error']}"
    else:
        d = fg["data"]
        line = (f"**Crypto Fear & Greed: {d['today']['value']} "
                f"({d['today']['classification']})**")
        dd = state.delta(ctx.get("prev") or {}, "fng", d["today"]["value"])
        if dd:
            line += f" · {dd[0]:+.0f} vs yesterday"
        if d["week_ago"]:
            delta = d["today"]["value"] - d["week_ago"]["value"]
            line += (f" · 7 days ago {d['week_ago']['value']} "
                     f"({d['week_ago']['classification']}), {delta:+d}")
        line += " · data via alternative.me"
    md.append(f"- {line}")
    html.append(f"<p>{_hb(line)}</p>")

    gl = ctx.get("global_mcap")
    if gl and gl["ok"]:
        d = gl["data"]
        line = (f"Total crypto market cap ${d['total_mcap_usd']/1e12:,.2f}T "
                f"({d['mcap_change_24h_pct']:+.2f}% 24h) · "
                f"BTC dominance {d['btc_dominance']:.1f}% · "
                f"ETH {d['eth_dominance']:.1f}%")
        md.append(f"- {line}")
        html.append(f"<p>{_hb(line)}</p>")
    md.append("")

    # ---- MACRO / EQUITIES ---------------------------------------------
    md.append("## MACRO & EQUITIES\n")
    html.append(_h_section("Macro &amp; Equities"))
    ca = ctx["cross_asset"]
    if not ca["ok"]:
        line = f"Cross-asset unavailable — {ca['error']}"
        md.append(line)
        html.append(f"<p><em>{_hb(line)}</em></p>")
    else:
        lines = []
        for label, q in ca["data"]["quotes"].items():
            chg = f"{q['pct_change']:+.2f}%" if q["pct_change"] is not None else "—"
            stamp = _as_of_stamp(q["as_of"], now)
            lines.append(f"**{label}** {q['last']:,.2f} · {chg}{stamp}")
        for l in lines:
            md.append(f"- {l}")
        html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in lines) + "</ul>")
        for label, err in (ca["data"].get("errors") or {}).items():
            md.append(f"- **{label}:** unavailable — {err}")
            html.append(f"<p><strong>{_esc(label)}:</strong> unavailable — {_esc(err)}</p>")
    md.append("")

    fed = ctx.get("fed_path")
    if fed is not None:
        line = (f"**Fed path:** {fed['data']}" if fed["ok"]
                else f"**Fed path:** unavailable — {fed['error']}")
        md.append(line + "\n")
        html.append(f"<p>{_hb(line)}</p>")

    # ---- RISK WINDOWS --------------------------------------------------
    windows = _risk_windows(ctx, today, now)
    md.append("## RISK WINDOWS (LIS)\n")
    html.append(_h_section("Risk Windows (LIS)"))
    for w in windows:
        md.append(f"- {w}")
    html.append("<ul>" + "".join(f"<li>{_hb(w)}</li>" for w in windows) + "</ul>")
    md.append("")

    failed = [k for k, v in ctx.items()
              if isinstance(v, dict) and v.get("ok") is False]
    if failed:
        note = "Degraded this run: " + ", ".join(sorted(failed))
        md.append(f"*{note}*")
        html.append(f"<p class='muted'><em>{_esc(note)}</em></p>")

    html.append(_h_close())
    return "\n".join(md), "\n".join(html)


def _run_note(run):
    if len(run) < 2:
        return "run direction unavailable"
    signs = [1 if v > 0 else (-1 if v < 0 else 0) for v in run]
    last, prior = signs[-1], signs[-2]
    # A flip only counts when the latest session reverses a run that was
    # already 3+ sessions the other way. Counting the CURRENT streak instead
    # would flag every steady run and stay silent on the actual reversals.
    streak = 0
    if last != 0 and prior != 0 and last != prior:
        for s in reversed(signs[:-1]):
            if s == prior:
                streak += 1
            else:
                break
    word = "inflow" if last > 0 else ("outflow" if last < 0 else "flat")
    note = f"{len(run)}-day run: " + ", ".join(f"{v:+,.0f}" for v in run)
    if streak >= 3:
        was = "inflow" if prior > 0 else "outflow"
        note += (f" — FLAG: sign flipped after {streak} consecutive "
                 f"sessions of {was}")
    return f"{note} (latest {word})"


def _options_line(d):
    n = d["nearest"]
    parts = [
        f"nearest expiry {n['expiry'].strftime('%d %b')} — max pain "
        f"${n['max_pain']:,.0f}, top call OI ${n['top_call_strike']:,.0f}, "
        f"top put OI ${n['top_put_strike']:,.0f}"
    ]
    if n["put_call_oi_ratio"] is not None:
        parts[0] += f", P/C OI {n['put_call_oi_ratio']:.2f}"
    m = d.get("monthly")
    if m and m["expiry"] != n["expiry"]:
        parts.append(
            f"monthly {m['expiry'].strftime('%d %b')} — max pain "
            f"${m['max_pain']:,.0f}, top call ${m['top_call_strike']:,.0f}, "
            f"top put ${m['top_put_strike']:,.0f}"
        )
    return " · ".join(parts)


def _setup_bullets(ctx):
    out = []
    c = ctx["crypto"]
    if c["ok"]:
        btc = next((p for p in c["data"]["pairs"] if p["symbol"] == "BTC"), None)
        if btc:
            # "% since 00:00 UTC" alone is a poor lead: early in the UTC day
            # it is near zero by construction, which reads as a quiet market
            # even when the 24h range says otherwise. Where price sits in that
            # range says more, and both are computable from the same ticker.
            # A true 24h change needs a 24h-ago price Kraken's ticker does not
            # carry; that arrives with the day-over-day state file.
            pos = _range_pos(btc)
            where = f", {pos:.0f}% up its 24h range" if pos is not None else ""
            # A real day-over-day move is the number that says whether
            # anything happened, so it leads when we have one. Without it the
            # honest fallback is where price sits in the 24h range: the
            # UTC-day figure is near zero by construction early in the day.
            d = state.delta(ctx.get("prev") or {}, "btc", btc["last"])
            lead = f", {d[1]:+.1f}% vs yesterday" if d else ""
            out.append(
                f"BTC ${btc['last']:,.0f}{lead}{where} "
                f"(${btc['low_24h']:,.0f}–${btc['high_24h']:,.0f})."
            )
    cal = ctx["calendar"]
    if cal["ok"]:
        todays = select_today(cal["data"]["events"], ctx["now"].date())
        usd_high = [e for e in todays
                    if e["impact"].lower() == "high" and e["country"] == "USD"]
        if usd_high:
            out.append(
                "Top USD risk today: " + ", ".join(
                    f"{e['title']} at {_hhmm(e['dt_lis'])} LIS" for e in usd_high[:3]
                ) + "."
            )
        else:
            out.append("No High-impact USD prints scheduled today.")
    f = ctx["flows_btc"]
    if f["ok"]:
        d = f["data"]
        out.append(
            f"BTC ETF net {_money(d['latest_total'])} on "
            f"{d['latest_date'].strftime('%d %b')}."
        )
    return out[:3] or ["Primary sources degraded this run — see sections below."]


# How far ahead the radar looks. Beyond about four months a date is not
# something to prepare for, it is trivia, and a section nobody reads is worse
# than one that does not exist.
RADAR_HORIZON_DAYS = 130


def radar_events(ctx, today):
    """Every dated policy event still ahead, both legs merged, nearest first.

    Two sources feed this. The Federal Register leg is fetched each run and
    knows about actions already signed. The watchlist leg is hand-kept and
    covers what no register can know - summits, announced deadlines, court
    terms. They are merged here rather than printed separately because the
    reader wants one ordered list of what is coming, not a lesson in where
    each date was stored.
    """
    horizon = today + timedelta(days=RADAR_HORIZON_DAYS)
    merged = []

    r = ctx.get("policy_radar")
    if r and r["ok"]:
        for e in r["data"]["events"]:
            merged.append({**e, "origin": "Federal Register", "stale": False})

    wl = ctx.get("watchlist") or {"events": []}
    for e in wl["events"]:
        merged.append({**e, "origin": "watchlist",
                       "label": e.get("tag") or "event",
                       "stale": watchlist.is_stale(e, today)})

    # A curated entry and a fetched one can describe the same action, and the
    # hand-written one is usually the short form of the official title - "FOMC
    # decision" against "FOMC decision + SEP and press conference". Comparing
    # fixed-length prefixes misses exactly that case, so compare whether the
    # shorter normalised title opens the longer one. Fetched entries are
    # considered first, so a collision keeps the copy with a primary-source
    # link and no staleness to track.
    kept = []
    for e in sorted(merged, key=lambda x: (x["date"],
                                           1 if x["origin"] == "watchlist"
                                           else 0)):
        if not (today <= e["date"] <= horizon):
            continue
        name = _norm_title(e["title"])
        if any(k["date"] == e["date"] and _same_event(name,
                                                      _norm_title(k["title"]))
               for k in kept):
            continue
        kept.append(e)
    return sorted(kept, key=lambda e: (e["date"], e["title"]))


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def _same_event(a: str, b: str) -> bool:
    """Whether two normalised titles on the same date name the same thing.

    Deliberately conservative: below 15 characters a shared opening is as
    likely to be coincidence as identity, and merging two genuinely different
    events would hide one of them completely.
    """
    short, long_ = sorted((a, b), key=len)
    return len(short) >= 15 and long_.startswith(short)


def _tminus(days: int) -> str:
    return "TODAY" if days == 0 else f"T-{days}"


def _radar_groups(events, today):
    """Split into the three horizons the reader actually acts on."""
    buckets = [("This week", []), ("Next 30 days", []), ("Later", [])]
    for e in events:
        days = (e["date"] - today).days
        idx = 0 if days <= 7 else (1 if days <= 30 else 2)
        buckets[idx][1].append((days, e))
    return [(name, rows) for name, rows in buckets if rows]


def _radar_text(days, e) -> str:
    """One event as a markdown line."""
    title = e["title"]
    if len(title) > 115:
        title = title[:114].rstrip() + "\u2026"
    head = f"**{_tminus(days)} \u00b7 {e['date']:%a %d %b}**"
    bits = [f"{head} \u2014 {title}"]
    label = e.get("label")
    if label and label != "event":
        bits.append(label)
    if e["origin"] == "watchlist" and e.get("stale"):
        seen = e.get("verified")
        bits.append(f"\u26a0 unconfirmed since {seen:%d %b}" if seen
                    else "\u26a0 never confirmed")
    return " \u00b7 ".join(bits)


def _risk_windows(ctx, today, now):
    """Windows still ahead of the reader, in order.

    Two rules the earlier version broke. A window that has already passed is
    not a risk window - the 28 Aug brief was built at 21:14 and still listed
    the 14:30 open and the 21:00 close as things to watch. And on a day the
    cash market never opens, an open and a close are not events at all.
    """
    timed, untimed = [], []

    cal = ctx["calendar"]
    if cal["ok"]:
        for e in select_today(cal["data"]["events"], today):
            if e["impact"].lower() == "high" or _is_cb_speaker(e["title"]):
                timed.append((e["dt_lis"],
                              f"**{_hhmm(e['dt_lis'])}** — {e['country']} "
                              f"{e['title']}"))

    # Weekend: the cash session does not exist, so neither do its windows.
    # Exchange holidays are NOT detected - that needs a holiday calendar we
    # do not have, so a holiday still shows an open and a close.
    weekend = today.weekday() >= 5
    if not weekend:
        # Recomputed, not assumed: the ET/Lisbon gap is not constant across
        # the two DST-mismatch windows in March and October.
        ny = ZoneInfo("America/New_York")
        open_et = datetime.combine(
            today, datetime.min.time(), tzinfo=ny).replace(hour=9, minute=30)
        close_et = open_et.replace(hour=16, minute=0)
        for dt_et, label in ((open_et, "NYSE cash open (09:30 ET)"),
                             (close_et, "NYSE cash close (16:00 ET)")):
            lis = dt_et.astimezone(LISBON)
            timed.append((lis, f"**{_hhmm(lis)}** — {label}"))

    o = ctx.get("options_btc")
    if o and o["ok"]:
        exp = o["data"]["nearest"]["expiry"]
        if exp == today:
            settle = datetime.combine(
                today, datetime.min.time(), tzinfo=UTC).replace(hour=8)
            lis = settle.astimezone(LISBON)
            timed.append((lis, f"**{_hhmm(lis)}** — Deribit expiry settles "
                               f"(08:00 UTC)"))
        else:
            untimed.append(f"Next Deribit expiry {exp:%a %d %b} 09:00 LIS")

    # A policy date that lands today or tomorrow belongs here as well as in
    # AHEAD. Counting down to a date for six weeks and then not mentioning it
    # among the day's risks on the morning it arrives would be the one failure
    # this whole section exists to prevent.
    for e in radar_events(ctx, today):
        days = (e["date"] - today).days
        if days > 1:
            break
        title = e["title"]
        if len(title) > 95:
            title = title[:94].rstrip() + "\u2026"
        untimed.append(f"**{'TODAY' if days == 0 else 'Tomorrow'}** — {title}")

    ahead = sorted((dt, txt) for dt, txt in timed if dt > now)
    passed = len(timed) - len(ahead)

    out = [txt for _, txt in ahead]
    if weekend:
        out.append("Cash equity markets closed today — no session windows.")
    if not ahead and not weekend:
        out.append(f"No windows left today; {passed} already passed at "
                   f"{_hhmm(now)} LIS.")
    elif passed:
        out.append(f"({passed} earlier window{'s' if passed > 1 else ''} "
                   f"already passed.)")
    return out + untimed


# ------------------------------------------------------------------- HTML

_CSS = """
body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
font-size:15px;line-height:1.55;color:#1a1a1a;max-width:720px;margin:0 auto;padding:12px}
h1{font-size:22px;margin:0 0 4px;letter-spacing:-.3px}
h2{font-size:13px;letter-spacing:1.2px;text-transform:uppercase;color:#444;
border-bottom:2px solid #1a1a1a;padding-bottom:5px;margin:24px 0 10px}
ul{margin:0;padding-left:20px}li{margin-bottom:6px}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0}
th{text-align:left;padding:6px 8px;border-bottom:1px solid #ccc;background:#f2f2f2}
td{padding:5px 8px;border-bottom:1px solid #eee}
tr.hi td{background:#fff8e1;font-weight:600}
p{margin:8px 0}.muted{color:#666;font-size:12.5px}
.sub{color:#666;font-style:italic;font-size:13px;margin:0 0 14px}
"""


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _hb(s):
    """Escape, then promote markdown bold to <strong>. Escaping happens first
    so content can never inject markup."""
    import re as _re
    return _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", _esc(s))


def _h_open(title, sub):
    return (f"<html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>"
            f"<h1>{_esc(title)}</h1><p class='sub'>{_esc(sub)}</p>")


def _h_section(name):
    return f"<h2>{name}</h2>"


def _h_table(headers, rows):
    out = ["<table><tr>"]
    out += [f"<th>{_esc(h)}</th>" for h in headers]
    out.append("</tr>")
    for r in rows:
        *cells, bold = r
        cls = " class='hi'" if bold else ""
        out.append(f"<tr{cls}>" + "".join(f"<td>{_esc(c)}</td>" for c in cells) + "</tr>")
    out.append("</table>")
    return "".join(out)


def _h_close():
    return "</body></html>"
