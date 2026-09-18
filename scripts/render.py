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
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import health
import state
import cycles
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


def _vs_label(ctx) -> str:
    """What the day-over-day comparison is actually against.

    state.delta compares today's figure against whatever the state file holds,
    and until 13 September 2026 all three callers labelled that "vs yesterday"
    no matter how old it was. On the morning after a missed brief that is
    simply untrue: the 13 Sep brief called a two-day move "vs yesterday",
    because the last state written was Friday's. The number was right and the
    label was wrong — the same class of error as §3.12, a true figure
    described as something it is not.

    The label now comes from the state file's own date, so it can only say
    what the comparison really is.
    """
    base = health.baseline_date(ctx.get("prev") or {})
    if base is None:
        return "vs last brief"
    days = (ctx["now"].date() - base).days
    if days == 1:
        return "vs yesterday"
    if days == 0:
        return "vs earlier today"
    if days < 0:
        # A state file dated in the future is a bug somewhere else. Still
        # compare, but do not put a date on it that would read as fact.
        return "vs last brief"
    return f"vs {base:%a %d %b}"


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

    # Anything wrong with the delivery system itself leads, ahead of the
    # market. §3.9 is why it sits here and is typeset differently: a warning
    # that reads like one more data line is a warning nobody sees.
    for note in ctx.get("health") or []:
        md.append(f"> **⚠ {note}**\n")
        html.append(f"<p class='warn'>⚠ {_esc(note)}</p>")

    # ================= TIER 1 — the first screen =========================
    # The redesign's whole bet: about fifteen lines that answer most mornings
    # on their own. Eleven sections typeset with equal authority is the
    # condition that let a $6bn buyback read as broken data (§3.9), and
    # adding sections to a flat list makes that worse rather than better.

    # ---- CLOCKS --------------------------------------------------------
    clocks = _clocks(now)
    md.append("## CLOCKS\n")
    html.append(_h_section("Clocks"))
    for l in clocks:
        md.append(f"- {l}")
    md.append("")
    html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in clocks) + "</ul>")

    # ---- THE SETUP -----------------------------------------------------
    setup = _setup_bullets(ctx)
    md.append("## THE SETUP\n")
    for b in setup:
        md.append(f"- {b}")
    md.append("")
    html.append(_h_section("The Setup"))
    html.append("<ul>" + "".join(f"<li>{_hb(b)}</li>" for b in setup) + "</ul>")

    # ---- CALENDAR ------------------------------------------------------
    # ---- TODAY ---------------------------------------------------------
    # CALENDAR and RISK WINDOWS merged. They were two lists of the same day
    # in two places, and the reader had to interleave them by hand to answer
    # the only question that matters at 09:20: what is still coming.
    windows = _risk_windows(ctx, today, now)
    md.append("## TODAY\n")
    html.append(_h_section("Today"))
    cal = ctx["calendar"]
    if not cal["ok"]:
        line = f"Calendar unavailable — {cal['error']}"
        md.append(f"- {line}")
        html.append(f"<ul><li><em>{_hb(line)}</em></li></ul>")
        for w in windows:
            md.append(f"- {w}")
        html.append("<ul>" + "".join(f"<li>{_hb(w)}</li>" for w in windows)
                    + "</ul>")
    else:
        for w in windows:
            md.append(f"- {w}")
        html.append("<ul>" + "".join(f"<li>{_hb(w)}</li>" for w in windows)
                    + "</ul>")
    md.append("")

    # ---- CYCLE ---------------------------------------------------------
    # Silent most mornings by design. Prints only when a recurring expiry is
    # inside its own lead window, which is what keeps a 365-day horizon from
    # flooding the page.
    cyc = _cycle_lines(today)
    if cyc:
        md.append("## CYCLE\n")
        html.append(_h_section("Cycle"))
        for l in cyc:
            md.append(f"- {l}")
        md.append("")
        html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in cyc)
                    + "</ul>")

    _tier(md, html, "Tier 2 — the standing picture")

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
            vs = f" · {d[1]:+.1f}% {_vs_label(ctx)}" if d else ""
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
        n = _streak(run)
        if n > 1:
            word = "inflow" if run[-1] > 0 else "outflow"
            line += f" · **{n}th straight {word}**"
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
        bits = [f"**{label} perp** {fund}"]
        # A rate per eight hours is abstract. The same number as an annual
        # carry is money, and it is the figure that decides whether holding
        # the position costs more than the move is worth.
        carry = _annualised(f8)
        if carry is not None:
            bits.append(f"{carry:+.1f}%/yr annualised")
        b = _basis(d)
        if b is not None:
            bits.append(f"basis {b:+.3f}% (live)")
        bits.append(oi_txt)
        bits.append(d["source"])
        dlines.append(" · ".join(bits))
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
            line += f" · {dd[0]:+.0f} {_vs_label(ctx)}"
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
        # D24: supply AND dominance, never dominance alone. Dominance is a
        # ratio and rises when the denominator falls, so a spike during a
        # selloff is mostly arithmetic. Supply is the figure that says whether
        # capital actually arrived.
        if d.get("stable_supply_usd") is not None:
            sl = (f"**Stablecoins** ${d['stable_supply_usd']/1e9:,.0f}bn supply "
                  f"· {d['stable_dominance']:.2f}% of total cap")
            legs = [f"USDT {d['usdt_dominance']:.2f}%"
                    if d.get("usdt_dominance") is not None else None,
                    f"USDC {d['usdc_dominance']:.2f}%"
                    if d.get("usdc_dominance") is not None else None]
            legs = [l for l in legs if l]
            if legs:
                sl += " · " + " · ".join(legs)
            md.append(f"- {sl}")
            html.append(f"<p>{_hb(sl)}</p>")
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
        # One glanceable line of directions above the detail. Layout only: it
        # names which way each moved and stops there. Calling the set
        # "risk-on" would be the brief's first opinion about the market, and
        # D3 and D9 both forbid that.
        arrows = _cross_asset_line(ca["data"]["quotes"])
        if arrows:
            md.append(f"- {arrows}")
            html.append(f"<p>{_hb(arrows)}</p>")
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

    _tier(md, html, "Tier 3 — the horizons")

    # ---- AHEAD ---------------------------------------------------------
    # Tier 3. It used to sit above CRYPTO so it could not be missed; the tier
    # structure does that job now, and forward-looking things belong together.
    radar = radar_events(ctx, today)
    md.append("## AHEAD\n")
    html.append(_h_section("Ahead"))

    # The forward calendar moved here from CALENDAR when TODAY absorbed the
    # rest of it. Data prints and policy dates are the same question asked at
    # two ranges, and splitting them across tiers made the reader look twice.
    if ctx["calendar"]["ok"]:
        fwd = select_forward(ctx["calendar"]["data"]["events"], today)
        md.append("**Next 5 sessions — High impact**\n")
        html.append("<p><strong>Next 5 sessions — High impact</strong></p>")
        if fwd:
            items = [f"{e['dt_lis'].strftime('%a %d %b')} {_hhmm(e['dt_lis'])} LIS | "
                     f"{e['country']} | {e['title']}" for e in fwd]
            for i in items:
                md.append(f"- {i}")
            html.append("<ul>" + "".join(f"<li>{_hb(i)}</li>" for i in items)
                        + "</ul>")
        else:
            # Distinguish an empty forward view from a dead feed. Printing
            # "none scheduled" when the fetch failed is the worst outcome: it
            # reads as an all-clear. ForexFactory publishes only the current
            # week, so late in the week it genuinely runs out.
            note = ("No further High-impact events this week. ForexFactory "
                    "publishes only the current week, so next week is not "
                    "covered." if ctx["calendar"]["data"].get("week_only")
                    else "None scheduled in the forward feed.")
            md.append(f"- {note}")
            html.append(f"<ul><li>{_hb(note)}</li></ul>")
        md.append("")

    md.append("**Policy & geopolitics**\n")
    html.append("<p><strong>Policy &amp; geopolitics</strong></p>")
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

    # ---- FED PATH ------------------------------------------------------
    # Above POLICY DESK: the rate and what is priced against it frame
    # everything underneath, including the buyback and supply lines.
    fed_lines, fed_notes = _fed_path(ctx, today)
    # Renamed from FED PATH: the section already carries more than the Fed's
    # path, and midterm control contracts come off the same Kalshi API.
    md.append("## EXPECTATIONS\n")
    html.append(_h_section("Expectations"))
    for l in fed_lines:
        md.append(f"- {l}")
    html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in fed_lines)
                + "</ul>")
    md.append("")
    if fed_notes:
        note = " · ".join(fed_notes)
        md.append(f"*{note}*\n")
        html.append(f"<p class='muted'><em>{_esc(note)}</em></p>")

    # ---- POLICY DESK ---------------------------------------------------
    # Warsh and Bessent, the two people whose decisions Kabil trades around.
    # Warsh is tracked by name off the Fed's own feeds. Bessent has no feed at
    # all - Treasury publishes none - so he is tracked through the operations
    # he controls: buybacks and the coupon calendar.
    fed_lines, ops_lines, desk_notes = _policy_desk(ctx, today)
    md.append("## POLICY DESK\n")
    html.append(_h_section("Policy Desk"))
    for label, lines in (("Fed \u00b7 Warsh & FOMC", fed_lines),
                         ("Treasury \u00b7 buybacks & supply", ops_lines)):
        if not lines:
            continue
        md.append(f"**{label}**\n")
        html.append(f"<p><strong>{_hb(label)}</strong></p>")
        for l in lines:
            md.append(f"- {l}")
        html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in lines)
                    + "</ul>")
        md.append("")
    note = ("Treasury publishes no press feed, so the secretary is tracked "
            "through operations rather than remarks.")
    if desk_notes:
        note += " " + " ".join(desk_notes)
    md.append(f"*{note}*\n")
    html.append(f"<p class='muted'><em>{_esc(note)}</em></p>")

    # ---- BACKDROP ------------------------------------------------------
    # Slow-moving series that frame everything above them. A brief is the
    # right place for numbers that do not move: by the time one has changed,
    # it has changed quietly, over weeks, and nobody was watching for it.
    bd = ctx.get("backdrop")
    if bd is not None:
        md.append("## BACKDROP\n")
        html.append(_h_section("Backdrop"))
        blines = _backdrop_lines(bd, now)
        for l in blines:
            md.append(f"- {l}")
        md.append("")
        html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in blines)
                    + "</ul>")
        if bd["ok"] and bd["data"].get("partial"):
            p = f"partial: {bd['data']['partial']}"
            md.append(f"*{p}*\n")
            html.append(f"<p class='muted'><em>{_esc(p)}</em></p>")

    # ---- NEWS ----------------------------------------------------------
    # The only section that is not a fetched number, which is why every item
    # is tagged with its source and its age, and why commentary is marked
    # apart from a wire (D16).
    nw = ctx.get("news")
    if nw is not None:
        md.append("## NEWS\n")
        html.append(_h_section("News"))
        nlines = _news_lines(nw, now)
        for l in nlines:
            md.append(f"- {l}")
        md.append("")
        html.append("<ul>" + "".join(f"<li>{_hb(l)}</li>" for l in nlines)
                    + "</ul>")
        if nw["ok"]:
            sub_ = ("Headlines, not data. A wire item is reported; a "
                    "ZeroHedge item is commentary and is marked as such.")
            if nw["data"].get("partial"):
                sub_ += f" partial: {nw['data']['partial']}"
            md.append(f"*{sub_}*\n")
            html.append(f"<p class='muted'><em>{_esc(sub_)}</em></p>")

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


def _backdrop_lines(bd, now):
    """FRED's slow series, each with the date it was actually observed."""
    if not bd["ok"]:
        return [f"Backdrop unavailable — {bd['error']}"]
    out = []
    for e in bd["data"]["series"]:
        if e["id"] == "CPIAUCSL":
            bits = ["**CPI**"]
            if e["yoy"] is not None:
                bits.append(f"{e['yoy']:+.1f}% y/y")
            if e["ann_3m"] is not None:
                # The three-month annualised turns faster than the yearly
                # rate, so it is the one that shows a trend changing rather
                # than a trend that has already changed.
                bits.append(f"{e['ann_3m']:+.1f}% 3m annualised")
            bits.append(f"as of {e['as_of']:%b %Y}")
            out.append(" · ".join(bits))
            continue
        bits = [f"**{e['label']}** {e['value']:.2f}{e['unit']}"]
        if e["prior"] is not None:
            move = e["value"] - e["prior"]
            bits.append(f"{move:+.2f} on the prior print")
        # Two of these are monthly and one is daily with a lag. Without the
        # date a slow number reads as today's, which is the misleading-because-
        # present failure rather than the missing-data one.
        bits.append(f"as of {e['as_of']:%d %b}")
        out.append(" · ".join(bits))
    if out:
        out.append(f"*{bd['data']['source']}*")
    return out


def _news_lines(nw, now):
    """Headlines, newest first, each carrying its source and its age."""
    if not nw["ok"]:
        return [f"News unavailable — {nw['error']}"]
    items = nw["data"]["items"]
    if not items:
        return [f"Nothing on the wire in the last "
                f"{nw['data']['window_hours']}h."]
    out = []
    for i in items:
        age = (now - i["when"]).total_seconds() / 3600
        stamp = f"{age:.0f}h ago" if age >= 1 else "under an hour"
        title = i["title"]
        if len(title) > 150:
            title = title[:149].rstrip() + "\u2026"
        # A commentary headline typeset like a wire item is an opinion wearing
        # a fetched number's clothes. The tag is the whole of D16.
        tag = (f"via {i['source']}" if i["kind"] == "wire"
               else f"**{i['source']} — commentary, not a wire**")
        out.append(f"**{stamp}** — {title} · {tag}")
    return out


def _cross_asset_line(quotes):
    """Every cross-asset move as one line of directions.

    Five scattered rows make the reader assemble the picture. This assembles
    the *directions* and nothing else — no verdict, no "risk-on", no reading
    of what the combination means. That reading is Kabil's, or it happens in
    chat where it is visibly a conversation and not a data feed.
    """
    bits = []
    for label, q in quotes.items():
        pct = q.get("pct_change")
        if pct is None:
            continue
        mark = "\u25b2" if pct > 0 else ("\u25bc" if pct < 0 else "\u2014")
        bits.append(f"{label} {mark}")
    return "**Cross-asset** \u2014 " + " \u00b7 ".join(bits) if bits else ""


def _annualised(funding_8h):
    """A funding rate stated as an annual carry.

    Three intervals a day, 365 days. Labelled *annualised*, never
    *projected*: it is arithmetic on the rate standing right now, not a claim
    that the rate persists. D9 forbids the second and this is not it.
    """
    if funding_8h is None:
        return None
    return funding_8h * 3 * 365 * 100


def _basis(perp):
    """Perp against index, in per cent. None when either side is missing.

    Funding is the rate for the interval that just ended, so it lags. Basis is
    where the contract is trading against the index **now**. The two get
    different labels for that reason.
    """
    mark = perp.get("mark_price") or perp.get("last_price")
    index = perp.get("index_price")
    if mark is None or not index:
        return None
    return (mark - index) / index * 100


def _strike_list(rows):
    """Top strikes as `$85,000 (2,140)`, biggest open interest first."""
    return " · ".join(f"${k:,.0f} ({v:,.0f})" for k, v in rows)


def _streak(run):
    """How many sessions the flow has kept the same sign. 0 if it has not."""
    if not run or run[-1] == 0:
        return 0
    sign = 1 if run[-1] > 0 else -1
    n = 0
    for v in reversed(run):
        if v == 0 or (1 if v > 0 else -1) != sign:
            break
        n += 1
    return n


def _options_line(d):
    n = d["nearest"]
    parts = [
        f"nearest expiry {n['expiry'].strftime('%d %b')} — max pain "
        f"${n['max_pain']:,.0f}"
    ]
    # Three strikes a side, biggest OI first, with the contract counts. Where
    # the open interest actually sits is fetched data; what price will do
    # about it is not, and stays unsaid (D3, D9).
    if n.get("top_calls"):
        parts[0] += f", calls {_strike_list(n['top_calls'])}"
    elif n.get("top_call_strike") is not None:
        parts[0] += f", top call OI ${n['top_call_strike']:,.0f}"
    if n.get("top_puts"):
        parts[0] += f", puts {_strike_list(n['top_puts'])}"
    elif n.get("top_put_strike") is not None:
        parts[0] += f", top put OI ${n['top_put_strike']:,.0f}"
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
            lead = f", {d[1]:+.1f}% {_vs_label(ctx)}" if d else ""
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
# 365, up from 130. §5's oldest open question - "is the AHEAD horizon right?"
# - is answered by giving each entry its own `lead` instead of one horizon for
# everything, so a year of range costs nothing in noise.
RADAR_HORIZON_DAYS = 365


def _bn(v):
    """Par amounts arrive in dollars and are always in the billions."""
    return "\u2014" if v is None else f"${v / 1e9:,.1f}bn"


def _policy_desk(ctx, today):
    """The two people and one operation Kabil follows, as printable lines.

    Returns (fed_lines, ops_lines, notes). Split so the renderer can tell a
    quiet week from a broken feed: an empty list and a failed fetch must not
    produce the same output.
    """
    fed_lines, ops_lines, notes = [], [], []

    off = ctx.get("fed_officials")
    if off and off["ok"]:
        d = off["data"]
        for i in d["items"][:5]:
            who = i["speaker"]
            title = i["title"]
            if len(title) > 150:
                title = title[:149].rstrip() + "\u2026"
            fed_lines.append(
                f"**{who}** {i['date']:%d %b} \u00b7 {title} \u00b7 {i['kind']}")
        if not d["items"]:
            fed_lines.append(
                f"No {' / '.join(d['watching'])} remarks or FOMC releases in "
                f"the last {d['lookback_days']} days.")
        if d.get("partial"):
            notes.append(f"Fed feeds partial: {d['partial']}")
    elif off:
        fed_lines.append(f"Fed feeds unavailable \u2014 {off['error']}")

    ops = ctx.get("treasury_ops")
    if ops and ops["ok"]:
        d = ops["data"]

        # Announced operations lead, and are worded as forthcoming. The 10 Sep
        # miss was not a missing number - it was a $6bn operation typeset
        # exactly like a finished one, under blank amounts it had not yet
        # earned. Anything still ahead now says so in its first two words.
        for a in d.get("announced", []):
            days = (a["date"] - today).days
            when = ("TODAY" if days == 0 else
                    "TOMORROW" if days == 1 else
                    f"{a['date']:%a %d %b}")
            bits = [f"**\u26a0 ANNOUNCED \u2014 buyback {when}**"]
            if a.get("opens") and a.get("closes"):
                bits.append(f"{_hhmm(a['opens'])}\u2013{_hhmm(a['closes'])} LIS")
            bits.append(f"up to {_bn(a.get('cap'))}"
                        if a.get("cap") else "size not yet published")
            if a.get("bucket"):
                bits.append(str(a["bucket"]))
            if a.get("settles"):
                bits.append(f"settles {a['settles']:%d %b}")
            line = " \u00b7 ".join(bits)
            if a.get("step_up") and a.get("norm"):
                # Name the bucket in the claim. "3.0x the norm" with no
                # qualifier invites the reader to compare it against every
                # other buyback line on the page, which is the mistake the
                # comparison itself was just fixed for.
                line += (f" \u2014 **{a['cap'] / a['norm']:.1f}\u00d7 the "
                         f"{_bn(a['norm'])} norm for this maturity bucket** "
                         f"(last {a.get('norm_n', 0)})")
            ops_lines.append(line)

        for b in d.get("completed", [])[:2]:
            bits = [f"**Buyback {b['date']:%d %b}**",
                    f"{_bn(b['accepted'])} accepted of {_bn(b['offered'])} offered"]
            if b.get("cap"):
                bits.append(f"cap {_bn(b['cap'])}")
            if b.get("bucket"):
                bits.append(str(b["bucket"]))
            ops_lines.append(" \u00b7 ".join(bits))

        if not d.get("announced") and not d.get("completed"):
            ops_lines.append("No buyback operations returned.")
        elif not d.get("announced"):
            ops_lines.append("No buyback operation currently announced.")

        if d["auctions"]:
            nxt = ", ".join(
                f"{a['date']:%a %d %b} {a['term']} {a['security_type']}"
                f"{' reopening' if a['reopening'] else ''}"
                for a in d["auctions"])
            ops_lines.append(f"**Next coupon auctions** \u00b7 {nxt}")
        else:
            ops_lines.append("No coupon auctions scheduled in the feed.")
        if d.get("partial"):
            notes.append(f"Treasury partial: {d['partial']}")
    elif ops:
        ops_lines.append(f"Treasury operations unavailable \u2014 {ops['error']}")

    return fed_lines, ops_lines, notes


def _last_fomc_statement(ctx):
    """When the FOMC last published a statement, if this brief saw one.

    POLICY DESK already fetches the Fed's monetary-policy feed, so this costs
    no request. An FOMC statement appearing in that feed is evidence a
    decision **landed** — §3.23's distinction, which round 16 paid for: a
    calendar says what is planned, only the data says what happened. The
    scheduled date on a watchlist line would not do, because a meeting can
    move and a statement cannot be published early.

    Only the statement counts. The same feed carries the projections release
    and the implementation note, and neither of those is the decision.

    The feed is read over a 21-day lookback, so a statement older than that is
    invisible here — which is harmless, because the staleness this guards
    against lasts one to two business days.
    """
    fed = ctx.get("fed_officials")
    if not (fed and fed.get("ok")):
        return None
    best = None
    for item in (fed["data"].get("items") or []):
        if item.get("kind") != "FOMC":
            continue
        if "fomc statement" not in (item.get("title") or "").lower():
            continue
        when = item.get("date")
        if isinstance(when, date) and (best is None or when > best):
            best = when
    return best


def superseded_range(rate_data, decided) -> bool:
    """Is the printed target range older than the last decision? (§3.24)

    The New York Fed carries `targetRateFrom`/`targetRateTo` on the **EFFR
    row**, and EFFR publishes one business day in arrears. So the range the
    brief prints is the one that was in force on the last day the effective
    rate was published — which trails the decision by a day or two, **eight
    times a year, on exactly the mornings that number matters most.**

    Observed live on 17 and 18 September 2026: the FOMC moved to 3.75–4.00%
    on the 16th and FED PATH printed `Target 3.50–3.75% · as of 16 Sep` for
    two mornings, correctly age-stamped and materially misleading. A reader
    would reasonably have concluded the Fed had held.

    `as_of` **equal** to the decision date is stale, not current: the decision
    lands at 19:00 Lisbon, so the rate in force for almost all of that day is
    still the old one.
    """
    if not decided:
        return False
    as_of = (rate_data or {}).get("as_of")
    if not isinstance(as_of, date):
        return False
    if rate_data.get("target_low") is None:
        return False
    return as_of <= decided


def _pct(v, places=2):
    return "\u2014" if v is None else f"{v:+.{places}f}%"


def _fed_path(ctx, today):
    """The rate picture: where the rate is, what is priced, and the last
    inflation prints that inform both.

    Deliberately absent: any statement of what the market will do on the
    decision. The brief reports what is priced and what was printed; turning
    that into an expected reaction is interpretation, and this project removed
    its interpretation layer to hold the zero-cost line. Printing a guess in
    the same typeface as a fetched number would undo every other guarantee
    here.
    """
    lines, notes = [], []

    rate = ctx.get("policy_rate")
    odds = ctx.get("fed_odds")

    if rate and rate["ok"]:
        d = rate["data"]
        decided = _last_fomc_statement(ctx)
        stale = superseded_range(d, decided)
        bits = []
        if d.get("target_low") is not None and d.get("target_high") is not None:
            bits.append(f"**Target {d['target_low']:.2f}\u2013{d['target_high']:.2f}%**")
            # The marker goes NEXT TO the number, not in a footnote. §3.9's
            # lesson: a $6bn buyback was present, sourced and correctly
            # stamped, and unreadable because the qualification was not where
            # the eye was.
            if stale:
                bits.append("\u26a0 **may be superseded**")
        if d.get("effr") is not None:
            bits.append(f"EFFR {d['effr']:.2f}%")
        if d.get("as_of"):
            bits.append(f"as of {d['as_of']:%d %b}")
        bits.append(d["source"])
        lines.append(" \u00b7 ".join(bits))
        if stale:
            notes.append(
                f"The target range above was in force on "
                f"{d['as_of']:%d %b}, and the FOMC published a statement on "
                f"{decided:%d %b} \u2014 so it may already have changed. The "
                f"New York Fed carries the range on its EFFR row, which "
                f"publishes one business day late. The decision itself is in "
                f"the statement under POLICY DESK")
    elif rate:
        lines.append(f"Policy rate unavailable \u2014 {rate['error']}")

    if odds and odds["ok"]:
        d = odds["data"]
        head = "**Priced for the next decision**"
        if d.get("closes"):
            days = (d["closes"].date() - today).days
            head += f" ({_tminus(days)}, settles {d['closes']:%a %d %b})"
        priced = " \u00b7 ".join(
            f"{o['label']} **{o['prob']:.0f}%**" for o in d["outcomes"][:4])
        lines.append(f"{head} \u2014 {priced}")

        # A book whose mids do not sum near 100 is too wide to quote as
        # probability, and saying so beats implying a precision the spread
        # does not support.
        if abs(d["raw_total"] - 100.0) > 8:
            notes.append(f"Kalshi mids sum to {d['raw_total']:.0f}%, not ~100% "
                         f"— wide book, treat these as indicative")
        widest = max((o["spread"] for o in d["outcomes"]
                      if o.get("spread") is not None), default=None)
        tail = d["source"]
        if widest is not None:
            tail += f", widest spread {widest:.0f}pp"
        lines.append(f"*{tail}*")
    elif odds:
        lines.append(f"Priced odds unavailable \u2014 {odds['error']}")

    infl = ctx.get("inflation")
    if infl and infl["ok"]:
        for p in infl["data"]["prints"]:
            age = ""
            # How stale the print is matters: these are monthly, and the same
            # number stands for weeks. Saying which month it is stops it
            # reading as today's news.
            flag = " *(preliminary)*" if p.get("preliminary") else ""
            lines.append(
                f"**{p['label']}** {p['period']}{flag} \u00b7 "
                f"{_pct(p['mom'])} m/m \u00b7 {_pct(p['yoy'], 1)} y/y{age}")
        if not infl["data"]["prints"]:
            lines.append("No inflation prints returned.")
        if infl["data"].get("partial"):
            notes.append(f"BLS partial: {infl['data']['partial']}")
    elif infl:
        lines.append(f"Inflation prints unavailable \u2014 {infl['error']}")

    return lines, notes


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
        # An entry outside its own lead window is not due yet. This is what
        # lets the horizon reach a year without the section flooding.
        if not watchlist.within_lead(e, today):
            continue
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


RADAR_BUCKETS = (("Now", 7), ("This month", 31), ("3 months", 92),
                 ("6 months", 183), ("12 months", 365))


def _radar_groups(events, today):
    """Split into the five horizons the reader acts on.

    Was three, capped at 130 days. An empty bucket is not printed, so a quiet
    year costs nothing.
    """
    buckets = [(name, []) for name, _ in RADAR_BUCKETS]
    for e in events:
        days = (e["date"] - today).days
        for idx, (_, limit) in enumerate(RADAR_BUCKETS):
            if days <= limit:
                buckets[idx][1].append((days, e))
                break
    return [(name, rows) for name, rows in buckets if rows]


def _radar_text(days, e) -> str:
    """One event as a markdown line."""
    title = e["title"]
    if len(title) > 190:
        title = title[:189].rstrip() + "\u2026"
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


SESSIONS = (
    # name, tz, open, close. Tokyo's lunch break is ignored on purpose: the
    # question this answers is "is Asia trading", not "is it mid-session".
    ("Tokyo", "Asia/Tokyo", (9, 0), (15, 0)),
    ("London", "Europe/London", (8, 0), (16, 30)),
    ("New York", "America/New_York", (9, 30), (16, 0)),
)


def _span(minutes: int) -> str:
    minutes = int(abs(minutes))
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}h{mins:02d}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


def _clocks(now):
    """Four clocks and the state of three sessions. Nothing is fetched.

    Kabil works in UTC, Lisbon, New York and Tokyo, and the brief has until
    now made him do the arithmetic. The session line is the part that
    matters: "New York opens in 5h" is the sentence a 09:20 reader actually
    wants, and it is not derivable at a glance from four numbers.

    Every offset is computed from the zone database, never assumed. The
    ET-to-Lisbon gap is 4, 5 or 6 hours depending on the week, and this
    project has already paid once for hardcoding it.
    """
    stamps = [f"**{_hhmm(now)} LIS**"]
    for label, zone in (("UTC", "UTC"), ("NY", "America/New_York"),
                        ("TYO", "Asia/Tokyo")):
        stamps.append(f"{_hhmm(now.astimezone(ZoneInfo(zone)))} {label}")

    states = []
    for name, zone, (oh, om), (ch, cm) in SESSIONS:
        tz = ZoneInfo(zone)
        local = now.astimezone(tz)
        opens = local.replace(hour=oh, minute=om, second=0, microsecond=0)
        closes = local.replace(hour=ch, minute=cm, second=0, microsecond=0)
        shut = (local.weekday() >= 5
                or (zone == "America/New_York"
                    and cycles.is_us_market_holiday(local.date())))
        if shut:
            states.append(f"{name} shut")
        elif local < opens:
            mins = (opens - local).total_seconds() / 60
            states.append(f"{name} opens in {_span(mins)}")
        elif local < closes:
            mins = (local - opens).total_seconds() / 60
            states.append(f"{name} open {_span(mins)}")
        else:
            mins = (local - closes).total_seconds() / 60
            states.append(f"{name} closed {_span(mins)} ago")
    return [" \u00b7 ".join(stamps), " \u00b7 ".join(states)]


def _cycle_lines(today):
    """Recurring expiries inside their own lead window. Nothing is fetched.

    Empty most days, and that is correct — a section that prints every
    morning stops being read. See scripts/cycles.py for the rules and for the
    08:00 UTC settlement problem this exists to surface.
    """
    lines = []
    if cycles.rolled_today(today):
        lines.append("\u26a0 **Front expiry rolled today** \u2014 Deribit "
                     "settled 08:00 UTC, twenty minutes before this brief "
                     "built. Max pain and OI below are the NEXT expiry, not "
                     "the one that just went off.")
    for e in cycles.upcoming(today):
        lines.append(f"**{_tminus(e['days'])} \u00b7 {e['date']:%a %d %b}** "
                     f"\u2014 {e['name']} \u00b7 {e['note']}")
    return lines


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
        # Every scheduled event, not only the High-impact ones. This section
        # merges what used to be CALENDAR and RISK WINDOWS, so dropping the
        # Mediums here would lose them entirely.
        for e in select_today(cal["data"]["events"], today):
            loud = e["impact"].lower() == "high" and e["country"] == "USD"
            loud = loud or _is_cb_speaker(e["title"])
            name = f"**{e['title']}**" if loud else e["title"]
            bits = [f"**{_hhmm(e['dt_lis'])}** — {e['country']} {name}"]
            # Forecast and previous ride the same line rather than a separate
            # table. A merged section cannot carry columns, and losing F/P
            # would make this a downgrade for the prints that matter most.
            if e.get("forecast") or e.get("previous"):
                bits.append(f"F {_dash(e['forecast'])} · P {_dash(e['previous'])}")
            if e["impact"].lower() != "low":
                bits.append(e["impact"])
            timed.append((e["dt_lis"], " · ".join(bits)))

    # Weekend: the cash session does not exist, so neither do its windows.
    # US market holidays are now detected too (scripts/cycles.py), closing a
    # gap this function's own comment flagged: before, a holiday still printed
    # an open and a close.
    holiday = cycles.us_market_holidays(today.year).get(today)
    weekend = today.weekday() >= 5 or bool(holiday)
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

    # A buyback running today is a timed event with a known window, so it
    # belongs among the day's windows and not only in POLICY DESK.
    ops = ctx.get("treasury_ops")
    if ops and ops["ok"]:
        for a in ops["data"].get("announced", []):
            if a["date"] != today or not a.get("opens"):
                continue
            size = f"up to {_bn(a['cap'])}" if a.get("cap") else "size TBD"
            label = (f"**{_hhmm(a['opens'])}** \u2014 Treasury buyback "
                     f"operation, {size}"
                     f"{', ' + str(a['bucket']) if a.get('bucket') else ''}")
            timed.append((a["opens"], label))

    # A policy date that lands today or tomorrow belongs here as well as in
    # AHEAD. Counting down to a date for six weeks and then not mentioning it
    # among the day's risks on the morning it arrives would be the one failure
    # this whole section exists to prevent.
    for e in radar_events(ctx, today):
        days = (e["date"] - today).days
        if days > 1:
            break
        title = e["title"]
        if len(title) > 150:
            title = title[:149].rstrip() + "\u2026"
        untimed.append(f"**{'TODAY' if days == 0 else 'Tomorrow'}** — {title}")

    ahead = sorted((dt, txt) for dt, txt in timed if dt > now)
    passed = len(timed) - len(ahead)

    out = [txt for _, txt in ahead]
    if holiday:
        out.append(f"US cash equity markets closed today — {holiday}. "
                   f"ETF creations and redemptions are a true zero, not a "
                   f"missing feed.")
    elif weekend:
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
p.warn{background:#fff4f4;border-left:4px solid #c0392b;color:#8e2b20;
font-weight:600;padding:9px 12px;margin:12px 0;border-radius:2px}
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


def _tier(md, html, label):
    """A quiet rule between tiers.

    Not a heading: headings here are section names, and inventing a fourth
    level would push every real section down. The point is only to tell the
    reader where the first screen ends.
    """
    md.append(f"---\n\n*{label}*\n")
    html.append(f"<hr><p class='muted'><em>{_esc(label)}</em></p>")


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
