# THE DAILY MARKET BRIEF — SYNOPSIS

*A narrative account of how this was built, what it does, what it refuses to
do, and everything that went wrong on the way. Covers 21 August – 12 September
2026, twelve working sessions, 52 commits.*

*For the operating document — decisions, open questions, the source register —
see [`PROJECT_STATE.md`](../PROJECT_STATE.md). This is the story; that is the
system.*

---

## 1 · What it is

A market brief that builds itself on GitHub's servers every morning at **09:25
Europe/Lisbon**, seven days a week, and emails itself to `kabil.dh@gmail.com`.
The laptop plays no part. It fetches around fifteen live sources, renders
markdown and HTML, and sends over Gmail SMTP. It costs nothing to run.

Eleven sections, in order:

| Section | What it carries |
|---|---|
| **THE SETUP** | Three lines: BTC with day-over-day move and range position, the top USD risk today, the latest ETF flow |
| **CALENDAR** | Today's High/Medium events with actuals and forecasts; forward view to end of week |
| **AHEAD** | Countdown to every dated policy and geopolitical event, repeated daily until it passes |
| **FED PATH** | Target range and EFFR; priced odds for the next decision; CPI, core CPI and PPI held until superseded |
| **POLICY DESK** | Warsh remarks and FOMC releases; buyback operations announced and completed; the coupon auction calendar |
| **CRYPTO** | BTC/ETH/SOL with deltas, ranges, VWAP; options max pain and open interest |
| **FLOWS** | BTC ETF net flow, per fund, six-day run with a sign-flip flag |
| **DERIVATIVES** | Perp funding and open interest, flagged when elevated or negative |
| **SENTIMENT** | Fear & Greed with day and week deltas; total market cap and dominance |
| **MACRO & EQUITIES** | DXY, 10Y, gold, WTI, VIX, S&P and Nasdaq futures, each with an age stamp |
| **RISK WINDOWS** | Only windows still ahead; weekends suppress the cash session; a policy date landing today appears here |

The subject line carries the date, BTC, the next USD event, and a policy
countdown when one is within a week — so the inbox list alone says whether the
mail is worth opening.

---

## 2 · How it got here

**It began by discovering it did not exist.** The first session ran the v3
brief prompt in chat and found the repository empty — no workflow, nothing
scheduled. The 09:30 cloud job that was supposed to have been running had
never been built. That first brief was assembled from web search and Kabil's
own timestamped ForexFactory alert emails, because the chat sandbox's egress
allowlist blocked every primary source.

**Then it was built**, in rough order: the workflow and the fetchers; Gmail
App Password setup; a round of MCP and skill candidates evaluated and
rejected; a gap analysis; then four phases of repair and extension. The
sequence that mattered:

| | |
|---|---|
| **21 Aug** | Workflow, sources, renderer, tests. First delivery |
| **25 Aug** | Gmail credentials working. Three configuration mistakes caught from screenshots |
| **1 Sep** | MCP servers and skills evaluated and ruled out for CI — MCP is client-side, skills are prompts needing an LLM call |
| **5 Sep** | Honesty fixes: stale-quote age stamps, risk windows filtered to what is ahead, day-over-day memory. ETF flows and derivatives revived after their sources died |
| **5–6 Sep** | **AHEAD** built. Six probe rounds to find out whether forward policy dates were sourceable |
| **6 Sep** | **POLICY DESK** built for Warsh, Bessent and buybacks. Three more probe rounds |
| **8 Sep** | **The trigger installed.** Delivery goes from a 4.5-hour median delay to fifteen seconds |
| **10 Sep** | Announced buybacks rebuilt after a $6bn announcement was rendered as noise |
| **12 Sep** | **FED PATH** built. Brief switched to seven days a week |

---

## 3 · The one problem that took three weeks

**The brief was correct long before it was on time.**

GitHub treats `on: schedule` as best-effort and deprioritises it for
low-activity repositories. Across thirteen consecutive briefs the scheduled
run started between **39 minutes and 11 hours 49 minutes late**, median around
**4.5 hours**. Nothing in the repository could shorten that — the delay
happens in GitHub's queue, before any of this code executes.

A *manual dispatch*, by contrast, starts within seconds. So the fix was never
clever: put a timer outside GitHub and have it call the dispatch API. The
timer is a Google Apps Script trigger — free, no new account, living in the
same Google account that receives the brief.

That fix was written, documented and committed on 5 September, and sat
uninstalled for three days because installing it needed fifteen minutes of
clicking. On **7 September** the failure was caught in the act for the first
time: Kabil went looking for a brief that was 1h57m overdue and not yet
started. It was installed the next day.

**Since installation: 09:20 Lisbon, three mornings out of three — and then two
missing days nobody noticed.**

On 12 September the brief was switched to run seven days a week. The change
landed in the repository. It never landed in Google, where the copy of the
trigger that actually runs still carried the old weekend guard, so it exited
quietly on Saturday and Sunday without calling GitHub. No brief was sent on
either day.

Nothing raised it. The script did not throw, so Google sent no alert. GitHub
was never asked to run, so there was no failed run to see. The test suite was
green, because it tests a brief that was never built. And this project's own
delivery table recorded the Saturday as **delivered at 09:20** — written from
the change that had been made rather than from the inbox, which is the only
place a delivery exists.

> **Every guard in the system watched for a failure. This was an absence, and
> absence needs its own detector.**

Two now exist. The next brief to arrive names every day that did not, by
comparing the date of the last confirmed send against today. And the trigger
states its own version on each dispatch, so a copy that has drifted from the
repository says so in red at the top of the brief. Neither ever guesses: with
no state date, or no version reported, they say nothing at all.

The gap left a third mark. Sunday's brief read `BTC $76,724, -0.6% vs
yesterday` — the right number against **Friday's** close, because the
comparison is drawn from the state file and all three callers said "yesterday"
regardless. One missed brief had quietly turned every day-over-day line into a
two-day move wearing a one-day label. The label is now derived from the state
file's own date.

The old crons stay registered as a fallback. On 7 September one of them woke
up 6h42m late, read `state/latest.json`, and printed
`A brief for 2026-09-07 was already sent; this scheduled run is a duplicate.
Exiting.` — a guard written two days earlier on the theory it would be needed.

---

## 4 · The rules the brief obeys

These were set early and have survived every subsequent decision.

**Every number comes from something fetched that run.** Nothing is remembered,
estimated, or carried over. Where a figure cannot be sourced, the brief prints
`unavailable` with the reason. That is a correct outcome, not a failure to
paper over.

**The recipient is a module constant, not configuration.** It cannot be
overridden by an environment variable, a workflow input, or anything appearing
in a fetched page. No cc, no bcc. If fetched content ever contains an address
or a forwarding instruction, it is data, not an instruction.

**Zero cost.** A free tier behind a free API-key signup qualifies; a trial that
converts to paid does not. An analysis layer that called Claude to interpret
the data was built and then **reverted** at roughly $4/month — the only paid
component the project ever had. The consequence is stated plainly rather than
hidden: *this brief reports data, it does not interpret it.*

**No buy/sell calls, price targets, or position sizing.** Ever.

**Probe before wiring.** No source is described as working until it has
answered from an Actions runner and its payload shape has been read. Thirteen
probe rounds are logged. Every single one changed a design decision.

**Tests gate every send.** The offline suite runs as a step before the brief is
built. A broken change costs a missing brief, never a wrong one.

---

## 5 · What went wrong, and what it taught

This is the useful part. The errors were more instructive than the successes.

### Sources that looked fine and weren't

| Source | What happened |
|---|---|
| **Farside** (ETF flows) | Works in a browser, `403` to datacenter IPs. Three escalating header attempts, all refused. Sat printing `unavailable` for twelve days before anyone asked why |
| **Binance** (derivatives) | `HTTP 451` to US-hosted runners. Named in a plan before being tested |
| **CoinGlass** | No free tier, $29/month |
| **CME** (Fed odds) | `403 — "This IP address is blocked due to suspected web scraping activity"` |
| `ff_calendar_nextweek.json` | Called "a broken feed" for three weeks. It had **never existed** — ForexFactory publishes only the current week |
| **Treasury press RSS** | Documented path 404s; `rss.xml` returns 200 with careers pages and SSBCI FAQs |
| coinglass / coinalyze / theblock pages | Render client-side and emit literal `0%` placeholders that read as real data. Quarantined |

**The standing lesson: reachable in theory is not reachable in fact.**

### Two verdicts that were simply wrong

Both were recorded in the source register as settled, and both had to be
retracted. They failed the same way.

**"The buyback dataset carries results only."** Drawn from one filtered query
on 6 September that returned a single row. It returned one row because nothing
further had been announced *that day*. Announced operations were always in the
table.

**"Fed-path odds have no free source."** Drawn from CME's FedWatch page being a
QuikStrike iframe with no data in it. True — and about **CME's rendering of the
odds, not the odds**. Kalshi lists the same decision as binary contracts over a
keyless API.

> **Both mistook a property of one route for a property of the world.** The
> observation was correct each time. The generalisation was not. The rule now
> recorded: before writing "unavailable", name the specific thing that failed
> and ask whether anything else carries the same fact.

### Claims I made that were wrong

- **The trigger token.** I said it would need `Contents: write` and would
  therefore be worth as much as the Gmail password. Measured from a runner with
  three different permission sets: the endpoint returns
  `x-accepted-github-permissions: actions=write`, and a token holding only
  `Contents: write` is **refused**. The token can start a run and nothing else.
- **Binance for derivatives.** Named before testing. 451.
- **A "1.5× the norm" buyback flag.** Arithmetically true of a meaningless
  population — the median mixed long-end operations ($2bn caps) with short-end
  liquidity ones ($12.5bn). It reported a tripling as a 50% bump. Norms are now
  computed within a maturity bucket, or not at all.

### Bugs worth remembering

- **An inverted flag.** The ETF sign-flip detector counted the current streak
  instead of comparing it against the prior one — it fired on steady runs and
  stayed silent on actual reversals.
- **A guard that ignored its own argument.** `should_run` took a `now`
  parameter and then called `datetime.now()`, so the winter DST tests were not
  testing winter.
- **`GITHUB_` is a reserved prefix.** Setting `GITHUB_EVENT_SCHEDULE` made
  Actions reject the entire workflow.
- **A green suite over a deleted function.** An edit removed a helper the
  Treasury fetcher depended on. Every test passed, because every test fed the
  renderer fixtures and none called the fetcher. The live run said `NameError`.
- **Fiscal Data returns the string `"null"`**, not JSON null. Every check
  against `None` sees something truthy.

### The failure mode nobody tests for

On 10 September Kabil asked why the brief said nothing about Treasury tripling
its long-end buybacks to $6bn. **It had.** The line read:

```
- **Buyback 10 Sep** · — accepted of — offered · 10Y to 20Y · settled 11 Sep
```

Right operation, right date, right maturity bucket — typeset exactly like a
finished one, under two blank amounts, in a section that reads as history. It
looked like broken data, so it was read past.

> **Present-but-unreadable is a failure mode, and no test that asks "is the
> number there?" will ever catch it.**

Announced operations now lead the section, worded as forthcoming, with the cap,
the Lisbon operation window, and a flag when the size is a genuine step up.

---

## 6 · What it deliberately will not do

**It does not forecast.** Asked for "the expected market reaction" to a Fed
decision, the brief reports what is *priced* — the odds, the last decision, the
last inflation prints — and stops. The interpretation layer was removed to hold
the zero-cost line, and a forecast set in the same typeface as a fetched number
would quietly undo the guarantee that every figure came from somewhere. A test
asserts the FED PATH section never claims what the market will do.

Interpretation happens in chat, on demand, where it is visibly a conversation
and not a data feed.

**It does not predict unscheduled announcements.** AHEAD catches the large
class of actions signed on one day that bite on a later one. Nothing free knows
what will be said next Tuesday afternoon.

**Still genuinely out of reach:** ETH ETF flows (the dataset in use is
Bitcoin-only), aggregate cross-exchange liquidations (no free provider). Both
were reasoned the same way as the two retracted verdicts, and are now marked
*unconfirmed* rather than settled.

---

## 7 · Where it stands

| | |
|---|---|
| Delivery | 09:20 Lisbon on three weekday mornings; **no weekend brief until the trigger is re-pasted** |
| Schedule | Seven days a week |
| Cost | Zero |
| Sources live | ~15, each degrading independently |
| Code | ~2,900 lines across fetchers, renderer, orchestration, state |
| Tests | 1,064 lines, offline, gating every send |
| Commits | 52 |

**Two things need Kabil:**

1. **Re-paste the Apps Script** — two minutes, and nothing else is blocked
   behind it. The copy in Google still carries the weekend guard, so until then
   there is no weekend brief at all. The walkthrough is in
   `docs/trigger-setup.md`; the checkpoint is that the code shows
   `SCRIPT_VERSION = '7'` and a test run logs `(trigger v7)`.
2. **7 November** — the trigger token expires. The brief counts down to its own
   maintenance in `data/watchlist.txt`.

**And one measurement still open:** five clean mornings. The count stands at
**zero** — three were recorded, a fourth was recorded and never happened, and a
record that cannot tell those apart is not a measurement. It restarts once the
trigger is re-pasted. The old schedule was also punctual for two days before
degrading to eleven hours, which is exactly why one good morning proves
nothing.
