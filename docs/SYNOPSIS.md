# THE DAILY MARKET BRIEF — SYNOPSIS

*A narrative account of how this was built, what it does, what it refuses to
do, and everything that went wrong on the way. Covers 21 August – 20 September
2026, twenty-nine working sessions.*

*For the operating document — decisions, open questions, the source register —
see [`PROJECT_STATE.md`](../PROJECT_STATE.md). This is the story; that is the
system.*

---

## 1 · What it is

**Two editions a day**, both built on GitHub's servers and emailed to
`kabil.dh@gmail.com`. The laptop plays no part. Twenty-one live sources,
rendered to markdown and HTML, sent over Gmail SMTP. It costs nothing to run.

| | Lands | Anchored to | Shape |
|---|---|---|---|
| **Morning** | 09:25 Europe/Lisbon, 7 days | a Lisbon hour | the full picture, three tiers |
| **PM** | 08:00 New York (13:00 Lisbon most weeks) | **New York**, not Lisbon | a delta against the morning |

The morning brief is in **three tiers**, and the tiers are the design:

**Tier 1 — the first screen.** `CLOCKS` (four zones, three session states) ·
`THE SETUP` (BTC with its day move and range position, today's top USD risk,
the latest ETF flow) · `TODAY` (session windows, data prints with forecast and
previous, anything dated landing today) · `CYCLE` (expiries, rolls, the CME
weekend gap).

**Tier 2 — the standing picture.** `CRYPTO` · `FLOWS` · `DERIVATIVES`
(funding as an annual carry, basis, open-interest change against price, OKX
liquidation counts and side skew) · `SENTIMENT` · `MACRO & EQUITIES`.

**Tier 3 — the horizons.** `AHEAD` (every dated policy and geopolitical event
out to a year, in five buckets) · `EXPECTATIONS` (target range, priced odds,
CPI/PPI) · `POLICY DESK` (Fed releases, Treasury buybacks, the auction
calendar) · `BACKDROP` (unemployment, the curve, inflation, and the three
liquidity plumbing lines) · `NEWS`.

**The PM edition is a delta, not a second brief.** A fixed spine — BTC and ETH
since 09:20, cross-asset, what is still dated today — and a `MATERIAL CHANGE`
body that only prints what crossed a threshold. Most afternoons it says *"No
material change since 09:20"*, which is a real answer. **At weekends it runs
crypto only** (D25): when every cross-asset quote is stale and timestamped, the
dead section is dropped and funding plus liquidations take the slot.

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
| **13 Sep** | Two briefs found missing. **The brief learns to notice its own absence** |
| **14–16 Sep** | The news question answered by probing it. FRED proved able to say *"came in at"*. Three clean mornings of five |
| **18 Sep** | **Delivery solved: five mornings of five at 09:20.** The same morning found the policy rate two days stale |

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

### The week the brief learned to watch itself

On 13 September the inbox was checked instead of the run log, and **two briefs
were missing** — Saturday the 12th and that Sunday. The project's own delivery
table had recorded the Saturday as *delivered at 09:20*.

The cause was mundane: the seven-day switch removed a weekend guard from the
trigger script in the repository, and the copy that actually runs — in a Google
account, updated by hand — still had it. So it woke up on Saturday, decided it
was the weekend, and exited without calling GitHub.

**What mattered was that six separate things could have caught it and none was
looking.**

| | |
|---|---|
| Apps Script emails on a throw | a clean exit is not a throw |
| GitHub shows failed runs | a run nobody requests is not a failed run |
| The workflow's own crons | still weekday-only in the checkout that ran |
| The test suite | green — it tests a brief that was never built |
| `state/latest.json` | held the 11th, and nothing compared it to today |
| The project file | recorded a delivery, written from intent not inbox |

> **Every guard watched for a failure. This was an absence, and absence needs
> its own detector.** A brief that is never sent cannot report that it was
> never sent — so the next one to arrive reports it instead.

Two now exist. The next brief names every day that did not arrive, by comparing
the date of the last confirmed send against today. And the trigger states its
own version on each dispatch, so a copy that has drifted from the repository
says so in red. Neither guesses: no state date, or no version reported, and
they say nothing at all.

**The gap left a third mark, and it is the one that would have been missed.**
Sunday's brief read `BTC $76,724, -0.6% vs yesterday`. Right number, wrong
label — that was the move since **Friday**, because the comparison is drawn
from the state file while all three callers said "yesterday" regardless. One
missed brief had quietly turned every day-over-day line into a two-day move
wearing a one-day label.

**And the sharpest detail came from Google's own dashboard.** The trigger page
showed the timer had fired that Sunday at 09:20:11, with an error rate of
**0%** — on a morning with no brief at all. The figure was accurate and
worthless: *ran without error* and *delivered* are different claims, and only
one of them matters.

### The news question, answered by probing it rather than arguing about it

Four X accounts were nominated as news sources. X killed its free API tier for
new developers in February 2026 — pay-per-use at $0.005 a read, roughly
$23–60/month for this — and Nitter is under cease-and-desist. So X fails the
zero-cost rule and the reachability bar at the same time.

But X is a *route*, not the fact. Probed at their primary sources:

| Account | Result |
|---|---|
| @zerohedge | ✅ live feed, 21.6h window |
| @WatcherGuru | ❌ 200, well-formed, fully timestamped — and **41.9 hours stale**, carrying equity stories on the crypto beat |
| @financialjuice | 🟡 no feed advertised at all |
| @DeItaone | ❌ relays a Bloomberg terminal; no free primary exists by design |

**CNBC, which nobody had suggested, beat three of the four** — 30 items, a
54.8-hour window, three hours fresh, with a Strait of Hormuz vessel strike in
it. The accounts were the route someone already knew; probing the fact found a
better one.

WatcherGuru is the instructive failure. Every freshness check in this project
measures a *quote's* age. Nothing measured a *feed's*. A 200 with perfectly
formed, fully timestamped items can still be reporting the day before
yesterday.

### Can it say what a number *came in* at?

A second daily edition at 14:00 Lisbon — 09:00 New York, thirty minutes after
the 08:30 prints and thirty before the opening bell — is only worth sending if
it can report an **actual**. The morning brief cannot: its calendar source is
schedule-only and carries no such field.

Three probe rounds against FRED settled it.

The key needs a real account, not just an email — but the reachability test ran
*first*, with a deliberately invalid key, so that nobody signed up for a host
that might have blocked datacenter IPs the way Farside, Binance and CME all
did. It answered `400 — "the value for variable api_key is not registered"`,
which is the good answer: the door opens, only the lock is shut.

Then the shape. FRED can return a value **as first published**, stamped with
its publication date — proven end to end on the Empire State survey, which had
published at 08:30 ET and reached FRED about **three minutes later**.

Two traps surfaced on the way, and both would have printed a wrong date:

- **The default "today" wanders.** Three calls across two days returned
  2026-09-04, 09-11 and 09-15. Every shipped request now names its own window.
- **The release calendar lists things that have not happened.** Asking for
  future dates returned 2,965 of them, and the FOMC release comes back dated
  every day from 26 to 31 December — for something that occurs eight times a
  year. *A calendar tells you what is planned; only the data tells you what
  happened.*

One test also came within a single field of proving nothing. Comparing a figure
as-first-published against as-it-stands-today returned the same number twice —
equally consistent with *never revised* and with *my parameters were silently
ignored*. What separated them was metadata nobody was comparing.

> **A test whose pass and fail look identical is not a test.**

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

### The system that was never being measured

The last thing this week found was not in the repository at all.

Closing the session, I went looking for anything scheduled to fire into a chat
that was about to be shut. What came back instead was a task nobody had
mentioned in three weeks of notes: **a scheduled job, created on the first day
of the project and still switched on, that runs every weekday morning and can
send email to the same inbox as the brief.**

It has never actually produced anything. It opens with a seasonal check —
*is Lisbon on summer time?* — and if the answer is yes it prints one line and
stops. Lisbon has been on summer time every single day this project has been
measured. Fourteen seconds from start to finish, five days a week, since
August.

**Lisbon goes back to winter time on 25 October.** From the Monday after, the
check stops stopping it, and the job starts doing what it was written to do: if
it finds the morning brief in the inbox it relays it into a chat, and **if it
does not find one, it builds its own from web searches and mails that instead.**
The next Fed decision is two days later.

Worse, the guard it relies on is half missing. Its own text says two jobs are
registered — a summer one and a winter one — and exactly one owns each day. A
full listing returns one. **The summer slot is gone, and the winter slot is the
one that wakes up.**

Nothing was broken by this. Nothing had to be fixed today. But it is the same
lesson as the missing weekend briefs, arriving from the other side:

> The brief now notices when it fails to arrive. **Nothing notices a second
> brief that arrives on its own.** A `(local build)` email would land in the
> same inbox, under a similar subject, assembled to a standard none of this
> work has ever reviewed — and every check that exists looks only at the
> repository.

It was written down, dated, and left switched on, because it belongs to Kabil's
account and his inbox, it cannot fire for another five weeks, and switching off
somebody's fallback is not a thing to do on your own initiative.

### One more thing arrived after this was written

On 18 September Kabil shared a full redesign, worked out in a separate chat the
day before: the morning brief reorganised into three tiers so the first screen
answers most days on its own, the horizon stretched from four months to a year,
and the second edition rebuilt from the ground up.

**That last one is a reversal, and an instructive one.** The second edition had
been designed to report the number *after* it prints — *"CPI came in at X"* —
and three rounds of probing went into proving it could. Kabil killed it in one
sentence: **he is already at the desk when data prints.** A brief that tells him
what is already on his screens is a brief he stops opening. So the edition moved
*earlier* — before the print, not after — and became a scan of what changed
overnight rather than a report of what just landed.

Most of the FRED work that survives is repurposed; some of it is simply spent.
That is written down rather than quietly dropped.

The plan also found something genuinely new: **the trigger token expires on
7 November, and nothing would notice.** The dispatch would die, the old slow
schedule would pick the brief up hours later, it would still arrive — and every
alarm the project has built would stay green while it slid back to the delay it
took three weeks to fix. That one is real; it was checked against the code
before it was written down. A second item in the same plan was checked the same
way and turned out to be **already fixed six versions ago** — which is the
reason to check.

The plan is in the repository as `BUILD_PLAN.md`, verbatim, with a note at the
top saying what has moved since. **None of it is built.**

### And then it was built

The plan sat unbuilt for one day. On 18 September the gate cleared, and the
first three things on its list went in.

**The brief has a shape now.** It used to be eleven sections of equal weight,
one after another, and the reader had to find what mattered. It is now three
tiers. The first is about fifteen lines and answers most mornings on its own:
four clocks and where each session is, the three-line setup, everything still
to come today, and any recurring expiry close enough to matter. The rest is
there when it is wanted.

Two lists became one. The calendar said what was scheduled and the risk
windows said when the market opened, in two different places, and the reader
had to interleave them by hand to answer the only question a 09:20 brief is
for: **what is still coming today.** Now that is one list.

The brief also learned some things it can work out for itself and never needs
to ask anyone: when the US market is shut, when options expire, and that on
the last Friday of every month the expiry it quotes has already settled twenty
minutes before the brief was built. That last one had been quietly wrong every
month.

**The stale Fed rate is fixed** — and here honesty costs something. By the
time the fix shipped, the New York Fed had caught up on its own and the number
was correct again. So the flag is written, tested seventeen ways, and **has
never been seen doing its job.** The next chance is 28 October. Writing that
down, rather than counting it as done, is the same discipline that caught the
missing briefs in the first place.

**Two bugs fell out of building rather than reading**, which is the argument
for building. One would have crashed the renderer on the first Fed morning —
a missing import on a line that no test could reach without an FOMC in the
data. The other was older and stranger: the test suite that guards every send
opens with *"No network"*, and one of its tests had been **opening a real
connection to Gmail and attempting a real login, on every run, for weeks.** It
never broke anything. It was also the entire reason the suite took three
minutes instead of a fifth of a second.

> A test suite that promises no network and makes a network call is a gate
> reporting a property it does not have — the same shape as the Fed rate
> docstring that claimed to be the decision itself. Both were true of the
> intention and false of the code.

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
| Delivery | ✅ **SOLVED, both editions.** Morning dispatched from Google carrying `TRIGGER_VERSION: 8`; PM fired at **12:00:09Z — 13:00 Lisbon to the second** |
| Fallback | ✅ **Proven in anger.** On 19 Sep the PM timer never fired and the cron fallback caught it at 16:26, with a banner naming the path and the cause |
| Schedule | Seven days a week, two editions |
| Cost | Zero |
| Sources | 21, fetched **lazily** — the PM edition takes about nine and never touches FRED |
| Code | ~5,280 lines across fetchers, renderer, orchestration, state, cycles, self-checks |
| Tests | 2,633 lines, **643 checks**, offline, 0.2s, gating every send |
| Commits | 127 |

**Nothing needs Kabil to keep either edition running.**

---

### What the last three days actually taught

Seven defects were found between 18 and 20 September. **Not one was found by
the test suite.** Every one was found by dispatching a run and reading the
output.

| | What was wrong | What the suite said |
|---|---|---|
| §3.33 | the PM cron fallback was **inert** | green — the test asserted a string was *present* |
| §3.34 | `BRIEF LATE` would have fired on **every** PM edition | green — no test ran it as the PM edition |
| §3.35 | Friday's session announced as today's | green — every PM fixture had no timestamp |
| §3.36 | the PM edition waited on FRED, which it never prints | green |
| §3.37 | the shadow log recorded **test dispatches** as editions | green |
| §3.38 | bank reserves printed as **three quadrillion dollars** | green — the fixture and the renderer agreed, and both were wrong |
| §3.39 | six news feeds built to the wrong specification | green |

> **A green suite is evidence about the fixtures, not about production.** §8's
> rule — *nothing is working until a runner says so* — paid for itself seven
> times in three days, and the corollary is the sharper half.

---

### The one that is worth reading twice

On 20 September Kabil asked whether the brief watches four accounts he
follows. It watched one, through its website — X costs $0.005 a read with no
free tier. He asked for headlines in both editions.

Two probe rounds chose sources on **cadence** — items per hour — because the PM
window is only about three and a half hours and a slow feed would be empty most
afternoons. The reasoning was sound and the metric was wrong. **Every account
he named is curated for relevance**, which is the whole reason he named them,
and relevance was never a criterion in either round. It appeared only as a
defect to filter afterwards: baseball, then Reuters ticker landing pages, then
Harry and Meghan.

The second round said so out loud and it was misread. `site:reuters.com/markets`
scored **best of five on cadence** while returning pages that carry no story at
all. *A metric that rates content-free pages as the top source is not a metric
with a scoping problem.*

He killed it the same day: *"it is not what i asked for."* Reverted
byte-identical, and §3.39 records the reversal rather than deleting it.

> **A high-cadence feed of things he does not care about is not closer to what
> he asked for than a slow one. It is further away.**

---

### Open, and none of it urgent

1. **What he checks every morning that the brief still does not carry.** Asked
   in the planning chat, still unanswered. **This is where the remaining value
   is** — the easy additions are exhausted, and the news attempt is what
   happens when that question gets answered by inference instead.
2. **The curated half of the radar** is still empty of everything he has not
   named. Owed since the beginning.
3. **The shadow log** (D20) needs about two weeks of real PM editions before
   v1's fixed thresholds can be replaced with range-scaled ones. It has one
   honest row; three test rows were removed on 20 Sep for measuring the wrong
   interval.
4. **The OKX contract multiplier** is unprobed, so liquidations print counts
   and side skew and no dollar figure.

**7 November** remains dated: the trigger token expires, and the brief counts
down to its own maintenance in `data/watchlist.txt`.
