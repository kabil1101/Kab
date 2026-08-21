"""Brief rendering: markdown for logs, HTML for the email body.

Formatting rules that matter:
  - Every printed time is Lisbon local, labelled LIS.
  - A step that could not be sourced prints "unavailable" with the reason.
    That is a correct outcome, not a failure to paper over.
  - No estimated or remembered figures ever reach this layer; the renderer
    can only print what a fetcher actually returned.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

LISBON = ZoneInfo("Europe/Lisbon")

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
            md.append("- None scheduled in the forward feed.")
            html.append("<ul><li>None scheduled in the forward feed.</li></ul>")
        md.append("")

    # ---- CRYPTO --------------------------------------------------------
    md.append("## CRYPTO\n")
    html.append(_h_section("Crypto"))
    c = ctx["crypto"]
    if not c["ok"]:
        md.append(f"Prices unavailable — {c['error']}\n")
        html.append(f"<p><em>Prices unavailable — {c['error']}</em></p>")
    else:
        lines = []
        for p in c["data"]["pairs"]:
            lines.append(
                f"**{p['symbol']}** ${p['last']:,.2f} · "
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
    for label, key in (("BTC ETF", "flows_btc"), ("ETH ETF", "flows_eth")):
        s = ctx[key]
        if not s["ok"]:
            line = f"**{label}:** unavailable — {s['error']}"
        else:
            d = s["data"]
            run = [r["total"] for r in d["recent"] if r["total"] is not None]
            line = (f"**{label}** {d['latest_date'].strftime('%d %b')}: "
                    f"{_money(d['latest_total'])} total · {_run_note(run)}")
            ibit = d["recent"][-1].get("ibit")
            fbtc = d["recent"][-1].get("fbtc")
            if ibit is not None or fbtc is not None:
                line += f" · IBIT {_money(ibit)} · FBTC {_money(fbtc)}"
        md.append(f"- {line}")
        html.append(f"<p>{_hb(line)}</p>")
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
            stamp = f" (as of {_hhmm(q['as_of'])} LIS)" if q["as_of"] else ""
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
    windows = _risk_windows(ctx, today)
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
            out.append(
                f"BTC ${btc['last']:,.0f}, {btc['pct_since_utc_midnight']:+.2f}% "
                f"since 00:00 UTC, 24h range "
                f"${btc['low_24h']:,.0f}–${btc['high_24h']:,.0f}."
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


def _risk_windows(ctx, today):
    w = []
    cal = ctx["calendar"]
    if cal["ok"]:
        todays = select_today(cal["data"]["events"], today)
        for e in todays:
            if e["impact"].lower() == "high" or _is_cb_speaker(e["title"]):
                w.append(f"**{_hhmm(e['dt_lis'])}** — {e['country']} {e['title']}")
    # NYSE cash open, recomputed rather than assumed: the ET/Lisbon gap is not
    # constant across the two DST-mismatch windows in March and October.
    ny = ZoneInfo("America/New_York")
    open_et = datetime.combine(today, datetime.min.time(), tzinfo=ny).replace(hour=9, minute=30)
    w.append(f"**{_hhmm(open_et.astimezone(LISBON))}** — NYSE cash open (09:30 ET)")
    close_et = open_et.replace(hour=16, minute=0)
    w.append(f"**{_hhmm(close_et.astimezone(LISBON))}** — NYSE cash close (16:00 ET)")
    o = ctx.get("options_btc")
    if o and o["ok"]:
        exp = o["data"]["nearest"]["expiry"]
        if exp == today:
            w.append("**09:00** — Deribit expiry settles (08:00 UTC)")
        else:
            w.append(f"Next Deribit expiry {exp.strftime('%a %d %b')} 09:00 LIS")
    return w


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
