"""The analysis layer: reads the fetched data and says what it means.

Everything else in this project is deterministic — a fetcher either returns a
real number or reports unavailable. This module is the one place a model
reasons, and it is bounded accordingly:

  - The deterministic fetchers stay the source of truth. Prices, calendar,
    options and flows come from `sources.py`; the model reads those figures,
    it does not re-derive them.
  - Anything the model retrieves itself must be labelled and dated, or not
    stated at all. This is the same rule the brief has always run on: a figure
    is either fetched this run or it is unavailable.
  - Retrieval is restricted to an allowlist. The quarantined sources are
    absent from it, so the quarantine is enforced structurally rather than by
    asking the model nicely. Coinglass pages emit literal `0%` placeholders
    that read as real data; OptionCharts is paywalled; the CME FedWatch page
    is a JS iframe with no probabilities in it. None can be reached from here.

Why the model can see things the runner cannot: `web_fetch` and `web_search`
execute on Anthropic's infrastructure, not on the GitHub Actions runner. The
runner's datacenter IP is refused by Farside with a 403 regardless of headers;
a fetch that originates elsewhere is not subject to that block.
"""

from __future__ import annotations

import os
import sys

MODEL = "claude-opus-5"

# Retrieval allowlist. Quarantined sources are deliberately absent — see the
# module docstring. `allowed_domains` and `blocked_domains` are mutually
# exclusive, so an allowlist is both the safer and the only correct shape.
ALLOWED_DOMAINS = [
    "farside.co.uk",          # BTC/ETH ETF flows - the standing gap
    "federalreserve.gov",     # primary source for policy
    "reuters.com",
    "apnews.com",
    "cnbc.com",
    "ft.com",
    "bloomberg.com",
    "coindesk.com",
    "tradingeconomics.com",
]

SYSTEM = """\
You are the market analyst for a daily pre-open brief written for one reader,
a systematic trader based in Lisbon. He already has the numbers. What he needs
from you is the read: what today's data implies, what is inconsistent with
what, and where the risk sits.

HARD RULES ON FIGURES

1. The DATA section you are given was fetched deterministically this run. Those
   figures are authoritative. Use them. Never restate one with a different
   value, and never round in a way that changes meaning.
2. Any figure you retrieve yourself must carry its source and a date, inline,
   e.g. "(Reuters, 24 Aug)". If you cannot establish when a number is from,
   omit it. An undated number is worse than a missing one — this domain
   recycles stale figures relentlessly.
3. Never estimate, never infer a number from memory, never fill a gap with a
   plausible value. A section marked unavailable stays unavailable unless you
   actually retrieved something.
4. If two sources disagree, say so and give both with their dates. Do not
   silently pick one.

HOW TO REASON

Weigh confirmation. A single indicator moving is noise; two or three pointing
the same way is a read. Say which ones agree, by name. Where only one moved,
call it a single-source signal rather than dressing it as a conclusion.

Judge the regime before the detail. Is this trending, ranging, or unwinding a
move? The same print means different things in each. State the regime in a
clause, then read today against it — a brief that reads identically every day
is not analysis.

Connect the cross-asset block to crypto rather than listing it. DXY, gold, WTI,
the 10-year, VIX and equity futures are in the data because they move crypto
beta. Say how they bear on it today, or leave them out. An unconnected list of
levels is something he can already see in the table below your section.

WHAT TO WRITE

Roughly 400-500 words of markdown, no headings above ###, in this order:

- **Read** — 3 to 5 sentences. What today's setup actually is. Lead with the
  thing that would change his positioning, not the biggest number.
- **Tensions** — anything in the data that does not fit together: a price
  move at odds with flows, positioning at odds with the calendar, two
  indicators pointing opposite ways, a cross-asset move crypto has not yet
  reflected. This is the highest-value section; be specific and cite the
  figures. If nothing genuinely conflicts, say so in one line rather than
  inventing tension.
- **Watch** — concrete levels, times (Lisbon, labelled LIS), and events that
  would confirm or break the read.

Prose, not bullets-of-numbers. He can read the table himself.

NEVER give buy/sell calls, price targets, or position sizing. Data, levels,
event risk, and what they imply — nothing that reads as an instruction to
trade. Do not attach confidence scores or probabilities to your own read: you
have no record of your historical accuracy, so any such number would be
invented, and an invented number that looks rigorous is the worst thing this
brief could carry.

RETRIEVAL

You may search and fetch to close the gaps the DATA section marks unavailable —
ETF flows are the standing one. Do it only where it adds something; two or
three retrievals is usually plenty. If a retrieval comes back empty, say the
gap remains open. Do not paper over it.
"""


def _fmt(v, spec=",.2f"):
    return format(v, spec) if isinstance(v, (int, float)) else "—"


def digest(ctx) -> str:
    """Compact, factual rendering of what was actually fetched.

    Deliberately plain: this is evidence handed to the analyst, not prose. A
    step that failed is stated as failed, with its reason, so the model can
    tell 'quiet' apart from 'blind'.
    """
    now = ctx["now"]
    lines = [f"AS OF: {now:%A %d %B %Y, %H:%M} Lisbon ({now.tzname()})", ""]

    def section(title, key, render_ok):
        s = ctx.get(key)
        if s is None:
            return
        lines.append(f"## {title}")
        if not s["ok"]:
            lines.append(f"UNAVAILABLE — {s['error']}")
        else:
            try:
                render_ok(s["data"])
            except Exception as exc:  # noqa: BLE001 - never break the digest
                lines.append(f"(could not summarise: {type(exc).__name__})")
        lines.append("")

    def _crypto(d):
        for p in d["pairs"]:
            lines.append(
                f"{p['symbol']}: ${_fmt(p['last'])} | "
                f"{p['pct_since_utc_midnight']:+.2f}% since 00:00 UTC | "
                f"24h range ${_fmt(p['low_24h'])}-${_fmt(p['high_24h'])} | "
                f"24h VWAP ${_fmt(p['vwap_24h'])}"
            )

    def _calendar(d):
        import render as _r
        today = now.date()
        todays = _r.select_today(d["events"], today)
        if not todays:
            lines.append("No High/Medium impact events today.")
        for e in todays:
            lines.append(
                f"{e['dt_lis']:%H:%M} LIS | {e['country']} | {e['title']} | "
                f"F: {e['forecast'] or '—'} | P: {e['previous'] or '—'} | "
                f"{e['impact']}"
            )
        fwd = _r.select_forward(d["events"], today)
        if fwd:
            lines.append("Next 5 sessions, High impact:")
            for e in fwd:
                lines.append(
                    f"  {e['dt_lis']:%a %d %b %H:%M} LIS | {e['country']} | "
                    f"{e['title']}")
        if d.get("next_week_error"):
            lines.append(
                f"  (forward feed unavailable — {d['next_week_error']}; next "
                f"week is NOT covered)")

    def _options(d):
        for label in ("nearest", "monthly"):
            o = d.get(label)
            if not o:
                continue
            lines.append(
                f"{label} expiry {o['expiry']:%d %b}: max pain "
                f"${_fmt(o['max_pain'], ',.0f')}, top call OI "
                f"${_fmt(o['top_call_strike'], ',.0f')}, top put OI "
                f"${_fmt(o['top_put_strike'], ',.0f')}, P/C OI "
                f"{_fmt(o['put_call_oi_ratio'])}"
            )

    def _fng(d):
        t = d["today"]
        line = f"Fear & Greed: {t['value']} ({t['classification']})"
        if d.get("week_ago"):
            w = d["week_ago"]
            line += (f" | 7 days ago {w['value']} ({w['classification']}), "
                     f"{t['value'] - w['value']:+d}")
        lines.append(line)

    def _flows(d):
        lines.append(f"Latest session {d['latest_date']:%d %b}: total "
                     f"{_fmt(d['latest_total'], ',.1f')} US$m")
        for r in d["recent"]:
            lines.append(f"  {r['date']:%d %b}: total "
                         f"{_fmt(r['total'], ',.1f')}")

    def _cross(d):
        for label, q in d["quotes"].items():
            chg = (f"{q['pct_change']:+.2f}%"
                   if q.get("pct_change") is not None else "—")
            stamp = f" (as of {q['as_of']:%H:%M} LIS)" if q.get("as_of") else ""
            lines.append(f"{label}: {_fmt(q['last'])} | {chg}{stamp}")
        for label, err in (d.get("errors") or {}).items():
            lines.append(f"{label}: UNAVAILABLE — {err}")

    def _global(d):
        lines.append(
            f"Total market cap ${d['total_mcap_usd'] / 1e12:,.2f}T "
            f"({d['mcap_change_24h_pct']:+.2f}% 24h) | BTC dominance "
            f"{d['btc_dominance']:.1f}% | ETH {d['eth_dominance']:.1f}%")

    section("CRYPTO PRICES (Kraken)", "crypto", _crypto)
    section("ECONOMIC CALENDAR (ForexFactory)", "calendar", _calendar)
    section("BTC OPTIONS (Deribit)", "options_btc", _options)
    section("BTC ETF FLOWS (Farside)", "flows_btc", _flows)
    section("ETH ETF FLOWS (Farside)", "flows_eth", _flows)
    section("SENTIMENT (alternative.me)", "fear_greed", _fng)
    section("MARKET STRUCTURE (CoinGecko)", "global_mcap", _global)
    section("CROSS-ASSET (Yahoo)", "cross_asset", _cross)

    return "\n".join(lines)


def analyse(ctx) -> str:
    """Return the analyst's markdown. Raises on failure; the caller wraps it."""
    import anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "missing repository secret: ANTHROPIC_API_KEY. Add it at Settings "
            "-> Secrets and variables -> Actions. See README.md.")

    client = anthropic.Anthropic()
    facts = digest(ctx)
    print(f"  analyst: {len(facts)} chars of fetched data -> {MODEL}",
          file=sys.stderr)

    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=16000,
        # Adaptive thinking is on by default for Opus 5; naming it is explicit
        # rather than load-bearing. Never send budget_tokens - 400 on this model.
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        # A policy decline would otherwise end the turn with no analysis at
        # all. Server-side fallback re-runs the same request on another model
        # inside the same call.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM,
        tools=[
            {
                "type": "web_search_20260209",
                "name": "web_search",
                "max_uses": 5,
                "allowed_domains": ALLOWED_DOMAINS,
            },
            {
                "type": "web_fetch_20260209",
                "name": "web_fetch",
                "max_uses": 5,
                "allowed_domains": ALLOWED_DOMAINS,
            },
        ],
        messages=[{
            "role": "user",
            "content": (
                "Here is everything fetched deterministically for today's "
                "brief. Write the analysis.\n\n"
                f"<data>\n{facts}\n</data>"
            ),
        }],
    ) as stream:
        response = stream.get_final_message()

    if response.stop_reason == "refusal":
        detail = getattr(response, "stop_details", None)
        raise RuntimeError(
            f"model declined: {getattr(detail, 'category', 'unknown')}")

    text = "\n".join(
        b.text for b in response.content if b.type == "text" and b.text.strip()
    ).strip()
    if not text:
        raise RuntimeError("model returned no text")

    u = response.usage
    print(f"  analyst: {u.input_tokens} in / {u.output_tokens} out",
          file=sys.stderr)
    return text
