# PROJECT STATE — DAILY MARKET BRIEF

| | |
|---|---|
| **Project** | Daily Market Brief — automated pre-market brief, cloud-built, emailed |
| **Owner** | Kabil Dahmen |
| **Repo** | `kabil1101/Kab` · branch `claude/daily-market-brief-kvfi35` (default) |
| **Session 1** | 2026-08-21 |
| **Status** | 🟢 Content complete · 🟢 Trigger v7 live · 🟢 **DELIVERY SOLVED — 5 of 5, gate 0 CLEARED** · 🟢 **§3.26 CLOSED — the brief now names its own lateness, proven live** · 🟢 **§3.25 CLOSED — the outside task is deleted** · 🟢 **§3.24 FIXED — the range now flags itself when a decision has overtaken it** · 🟢 **three tiers live: CLOCKS, TODAY, CYCLE** · 🟢 **LIQUIDATIONS ARE FREE — OKX answers keyless with sizes and sides (§12.12)** · 🟢 **PM edition and state bundle live (Commit 4)** · 🟢 **Commit 5 — PM timers installed (3 confirmed)** · 🟡 **v8 banner clears on a dispatch carrying v8; the INSTALLED copy is unproven until Google dispatches** · 🟠 **seven bugs found by running it, all fixed (§3.33–§3.38)** · 🟢 **COMMIT 5 CLOSED — v8 proven from Google's own dispatch, PM landed 13:00 on the dot** · 🟢 **weekend PM edition is crypto only (D25)** · 📋 **build order in §13** |
| **Last updated** | 2026-09-20 |
| **Revision** | 30 (was: 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6) |

> ⚠ **MANDATORY.** Never overwrite a value in this file. The old one stays visible
> as `was:`. Every edit gets a §11 change-log entry with a type and an evidence
> line — **a change with no evidence line is not a valid change.** Increment the
> revision. Typo fixes included.

> ⚠ **THE RECURRING FAILURE IN THIS DOMAIN: reachable in theory is not reachable
> in fact.** Farside is a plain public page that works in a browser and returns
> 403 to a datacenter IP. Binance's public API returns 451 to US runners.
> `ff_calendar_nextweek.json` was called "a broken feed" for three weeks and had
> never existed. The Federal Register's `effective_on` field is populated for 0
> of 21 presidential documents. **No source enters this brief until it has
> answered a probe from an Actions runner and its payload shape has been read.**
> Nine probe rounds are logged in §12.2. Every one of them changed a design.

---

## §1 · WHERE THINGS STAND

The brief builds itself in GitHub Actions **seven days a week** (was, rev 1–5:
"every weekday"), fetches around eighteen live sources, renders markdown and
HTML, and emails `kabil.dh@gmail.com` over Gmail SMTP. It runs with the laptop
shut. **Eleven sections** (was: nine) — THE SETUP, CALENDAR, AHEAD, FED PATH,
POLICY DESK, CRYPTO, FLOWS, DERIVATIVES, SENTIMENT, MACRO & EQUITIES, RISK
WINDOWS — all live-verified in real runs, all degrading to a named
`unavailable` rather than a fabricated number.

**The diagnosis.** *(was, rev 1–2: "a delivery problem, not a content problem,
blocked on one person for one quarter of an hour" — that block cleared on
2026-09-08.)* Everything that was ever wrong with the content was fixed and
tested; what had never been fixed was when it arrived, because GitHub's
scheduler queued the job for a median of 4.5 hours before any of this code ran.
The external trigger that bypasses that is now **installed and proven end to
end**: Google Apps Script dispatched at 13:27 Lisbon, GitHub accepted it, and
run #44 completed 15 seconds later (§2.1b).

The project therefore moves from building to **measuring**. Fourteen briefs of
history say a scheduler can look fine for two days and then degrade, so a
single punctual morning proves nothing. *(was, rev 3–6: "blocked on nothing but
the passage of five weekday mornings.")*

**And then the measurement itself turned out to be wrong.** On 2026-09-13 the
inbox was checked for the first time rather than the run log, and two briefs —
Sat 12 and Sun 13 September — had never been sent at all. §2.1d had recorded
the Saturday as delivered at 09:20. It had not been. The cause is the one this
file predicted in rev 6 and then failed to verify: the Apps Script in Kabil's
Google account still carries the weekend guard that was removed from the
repository, so it exits cleanly every Saturday and Sunday without dispatching.

**The lesson is not "re-paste the script." It is that this project had no way
to detect its own absence** — a brief that is never sent cannot report that it
was never sent, Apps Script only emails on a throw, and GitHub only shows runs
someone asked for. Rev 7 closes that: the next brief to arrive names the days
that did not, and a stale trigger identifies itself. *(was, rev 7–9: "the
blocking item is a two-minute re-paste by Kabil" — done the same day, §2.1f.)*

**Where it stands now, 2026-09-18 — the measurement is closed.** *(was, rev
16–19: "Where it stands now, 2026-09-16 … Three mornings of five have landed at
09:20 Lisbon … Two mornings remain.")* Five mornings of five landed at 09:20
Lisbon, every one read from the inbox before the run log, against a scheduler
that was late 13 times out of 13. Delivery is solved (§2.1h). The trigger is
live at v7, the timer is confirmed, and the dispatch second was identical on
all five days. FRED's method is settled, the news set is decided, and the
second edition is designed, costed and approved.

**And the morning that closed the measurement opened something worse.** FED
PATH had been printing a target range the Fed superseded two days earlier —
present, sourced, correctly age-stamped and materially misleading (§3.24). So
the build queue that five clean mornings was supposed to unlock stays shut,
because a policy-critical bug in the brief that *ships* outranks three
additions to it. **The next FOMC is 28 October.**

**A second thing surfaced the same day, from outside the repository.** A
scheduled Cowork task has been firing every weekday since August and exiting
fourteen seconds later on a seasonal guard. It stops exiting on 26 October
(§3.25). Nothing in this file knew it existed, because everything in this file
measures the repository and **the repository is not the whole system.**

**This is still a sequencing problem, not a capability problem.** The
capability is demonstrated. The discipline being tested is whether a proven
improvement can wait behind a known defect — the same discipline §8's
comfortable-work trap describes, arriving from the opposite direction: not
"build something easier instead", but "build something ready too early".

---

## §2 · VERIFIED DATA

### §2.0 Confidence markers

| Marker | Meaning |
|---|---|
| ✅ CONFIRMED | Observed directly in a run log or a live brief this project produced |
| 📄 REPORTED | Measured in an earlier session, not re-measured since |
| ❓ UNKNOWN | Not established |

### §2.1 Delivery latency — the core measurement

| Metric | Value | Confidence |
|---|---|---|
| Consecutive scheduled briefs that arrived late | **13 of 13** (was: 12 of 12) | ✅ CONFIRMED for the 13th (2026-09-07, §2.1a) |
| Best | 39 min late | 📄 REPORTED |
| Median | ~4.5 h late | 📄 REPORTED |
| Worst | 11 h 49 m late | 📄 REPORTED |
| Manual dispatch latency | seconds | ✅ CONFIRMED (every dispatch, sessions 6–8, incl. 2026-09-07) |
| Target | 09:25 Europe/Lisbon | — |
| Consecutive on-time mornings, confirmed from the inbox | **3** (Wed 9 – Fri 11 Sep), then a 2-day gap | ✅ CONFIRMED (§2.1d, Gmail) |
| **Delivered-vs-target, five consecutive mornings** | **09:20 LIS, 5 of 5, Mon 14 – Fri 18 Sep** (was: ❓ UNKNOWN since rev 1) | ✅ **CONFIRMED — §2.1h, five inbox timestamps** |
| **Delivered-vs-target over a full week with the fix installed** | ✅ **SOLVED 2026-09-18** (was: ❓ UNKNOWN since rev 1; "restarts once the trigger is re-pasted" at rev 7) | **the measurement that decided it. It is decided** |

The 39-minute figure is the trap: the schedule was near-punctual on its first
two days and then degraded. **One good morning proves nothing.**

### §2.1a Monday 2026-09-07 — the failure observed directly

Kabil reported no brief. Checked rather than assumed:

| Fact | Value |
|---|---|
| Target | 08:25 UTC (09:25 Lisbon) |
| Checked at | 10:22 UTC (11:22 Lisbon) — **1h57m past target** |
| Scheduled runs started today | **none** |
| Workflow state | `active` — not disabled |
| Last run of any kind | 2026-09-06 16:46 UTC (a push-triggered test) |
| Last scheduled run ever | 2026-09-04 13:36 UTC — **4h11m late** |
| Prior three weekdays' scheduled starts | 12:47, 13:36 (4 Sep) · 12:53, 13:39 (3 Sep) · 13:44 (2 Sep) UTC — both cron slots firing, one exiting via the slot guard as designed |
| Resolution | dispatched manually at 10:22 UTC; delivered in ~2 min |

✅ CONFIRMED: nothing in this repository failed. The workflow is enabled, the
code is unchanged since a successful run, and the cron entry is correct. GitHub
simply had not started the job two hours after its scheduled time — the same
behaviour measured across the previous twelve briefs, on a day when it happened
to be visible because someone was waiting for it.

**This is the first time the failure was observed live rather than
reconstructed from timestamps afterwards.** It is also the clearest possible
statement of §1: the content was correct and ready at 09:25; nobody had asked
GitHub to run it.

### §2.1b Trigger installed — 2026-09-08

| Fact | Evidence |
|---|---|
| Apps Script `testNow` log | `Brief dispatched 13:27 LIS.` |
| GitHub side | run #44, `2026-09-08T12:27:42Z`, `workflow_dispatch`, success |
| Latency, Google click → run complete | **~15 seconds** (vs. a 4.5h median for the schedule) |
| Daily trigger | one time-based trigger, `sendBrief`, day timer 9–10am, project timezone Europe/Lisbon |
| Token | fine-grained, `Actions: write` + `Metadata: read`, repo `kabil1101/Kab` only, expires **2026-11-07** |

✅ CONFIRMED end to end. Every link in the chain — Google's timer, the token,
the dispatch endpoint, the workflow, the email — has now run in production.

### §2.1c The duplicate guard, proven in production — 2026-09-07

The brief was sent manually at 10:22 UTC. GitHub's scheduled run finally
started at 15:07 UTC, 6h42m late, and printed:

```
A brief for 2026-09-07 was already sent; this scheduled run is a duplicate. Exiting.
```

✅ CONFIRMED: `state.already_sent_today` works against a real late run. This is
the mechanism that stops the crons delivering a second, staler copy every
afternoon now that the trigger sends first. It was written on 2026-09-05 on the
theory that it would be needed; two days later it was.

### §2.1d Delivery, days 1–5 with the trigger live — **corrected 2026-09-13**

Rebuilt from the **inbox**, which is the only record of a delivery. The rows
below that changed were taken from what the trigger was expected to do.

| Day | Brief in inbox (Gmail) | Dispatch run | vs 09:25 target |
|---|---|---|---|
| Tue 2026-09-08 | 13:28 LIS | #44, manual `testNow` | trigger installed, not a scheduled morning |
| Wed 2026-09-09 | 09:20 LIS | #47, 08:20:13Z | ✅ |
| Thu 2026-09-10 | 09:20 LIS | #50, 08:20:14Z | ✅ **5 min early** |
| Fri 2026-09-11 | 09:20 LIS | #56, 08:20:14Z | ✅ |
| **Sat 2026-09-12** | **none — no brief was sent** (was: "09:20 LIS ✅") | **no dispatch fired**; the only run was #59 11:45Z, a `skip_email` dry-run | ❌ **MISSED** |
| **Sun 2026-09-13** | 13:38 LIS, dispatched by hand this session | #60 | ❌ **MISSED at target** |

**Three clean mornings, not four** (was: "Four clean mornings of the five §5
asks for. Monday closes it."). The counter restarts when the trigger is
re-pasted.

**Evidence.** Gmail `subject:"Market Brief"` for 5–13 Sep returns eight
messages; there is none dated 12 Sep and none dated 13 Sep before the manual
dispatch at 12:38 UTC. The Actions run list for `market-brief.yml` shows no run
at all on 12 Sep other than #59, and none on 13 Sep before #60.

### §2.1h The five clean mornings — the measurement itself

The count §5 has headed since rev 3. Restarted at zero on 2026-09-14 after
rev 7 found a recorded morning that never happened. **Every row is read from
the inbox first, then corroborated against the run log — never the other way
round** (§3.17, §8).

| # | Day | In inbox | vs 09:25 | Dispatch | Banner | Delta label |
|---|---|---|---|---|---|---|
| 1 | Mon 2026-09-14 | **09:20 LIS** (08:20:37Z) | ✅ 5 min early | #65 `workflow_dispatch` **08:20:13Z** — the Google timer | none | `+0.8% vs yesterday`, state dated 09-13 ✅ |
| 2 | Tue 2026-09-15 | **09:20 LIS** (08:20:38Z) | ✅ 5 min early | #68 `workflow_dispatch` **08:20:13Z** | none | `-1.2% vs yesterday`, state dated 09-14 ✅ |
| 3 | Wed 2026-09-16 | **09:20 LIS** (08:20:29Z) | ✅ 5 min early | #71 `workflow_dispatch` **08:20:13Z** | none | `-1.8% vs yesterday`, state dated 09-15 ✅ |
| 4 | Thu 2026-09-17 | **09:20 LIS** (08:20:36Z) | ✅ 5 min early | #74 `workflow_dispatch` **08:20:13Z** | none | `+1.3% vs yesterday`, state dated 09-16 ✅ |
| 5 | Fri 2026-09-18 | **09:20 LIS** (08:20:33Z) | ✅ 5 min early | #77 `workflow_dispatch` **08:20:13Z** | none | `+1.8% vs yesterday`, state dated 09-17 ✅ |

**5 of 5. The measurement §5 has headed since rev 3 is closed.** Five inbox
timestamps: `08:20:37Z`, `08:20:38Z`, `08:20:29Z`, `08:20:36Z`, `08:20:33Z` —
every one 09:20 Lisbon, five minutes ahead of the 09:25 target, against a
scheduler that was 13-for-13 late with a 4.5-hour median. No banner on any day.
Every delta label correct.

**Dispatch fired at 08:20:13Z on all five days.** Google documents
`nearMinute(25)` as ±15 minutes. **The promise in `docs/trigger-setup.md`
— "expect the brief between roughly 09:10 and 09:40" — is deliberately NOT
narrowed.** Five samples describe observed behaviour; ±15 minutes is the
vendor's stated contract, and five observations do not override it. Narrowing
it would teach Kabil to read a 09:35 arrival as a fault when it would be
within spec. The observation is recorded; the promise stays wide.

**Day 1 carried more than a tick.** Run #65 executed at `616aaaf` — the head
holding every change made on 13 Sep: `health.py`, `_vs_label`, the
`trigger_version` workflow input. **The delivery path survived all of it
through a real morning**, which is the thing a green offline suite could not
tell us (§3.11).

The duplicate guard also fired again unprompted: run #63 (13 Sep 13:50Z,
`schedule`) exited on `last_sent_date`, and run #67 (14 Sep 15:57Z) did the
same. D5's fallback continues to cost nothing while the trigger wins the race.

**Day 2 added a measurement nobody asked for.** Both dispatches fired at
**08:20:13Z — the same second, two days running.** Google documents
`nearMinute(25)` as ±15 minutes and §12.2's setup doc repeats that, so the
expected spread was up to half an hour. Two identical samples suggest the timer
is far tighter in practice than its own documentation promises. **Two samples
are not a claim** — this gets revisited at day 5, and if it holds, the setup
doc's "expect the brief between roughly 09:10 and 09:40" is understated and
should be corrected rather than left as a safe over-estimate.

**Day 4 answered the question day 3 raised: does the brief move on?** It does.
`Priced for the next decision (T-41, settles Wed 28 Oct) — Fed maintains rate
56% · Hike 25bps 46%`. The countdown re-pointed at October and Kalshi rolled to
the next meeting's contracts without intervention. POLICY DESK also picked up
both of yesterday's Fed releases from the RSS leg — the statement and the
economic projections — so the decision is recorded as history in the right
section rather than lingering as a forecast in the wrong one.

**And the announced-buyback rebuild fired on a live operation.** The section
led with `⚠ ANNOUNCED — buyback TODAY · 18:40–19:00 LIS · up to $4.0bn · 7Y to
10Y · settles 18 Sep`, and the same operation appeared in RISK WINDOWS at
18:40. That is §3.9's fix working on a real announcement — the failure mode
being a $6bn operation rendered as two blank amounts under a completed-looking
line on 10 Sep. **Worded as forthcoming, carrying its cap and its Lisbon
window, leading the section.** First time it has been observed doing that
outside a dry-run.

⚠ **One item not verified:** the `Target …% · EFFR …` line sits above the
portion of the run log that was read, so whether the target range reflects
yesterday's decision is **unchecked, not confirmed**. Day 5 reads it. Saying
"it moved on correctly" on the strength of the line below it would be exactly
the §3.17 error.

**Day 3 was the FOMC, and it is the best evidence yet that the sections do
their job.** Both legs of the policy radar fired on the same event and agreed:
the ForexFactory calendar made *Federal Funds Rate 19:00* the top USD risk, and
the hand-kept watchlist entry reached T-0 as `TODAY FOMC decision + SEP / dot
plot`. **Both appear in the subject line**, so the inbox list alone said the
decision was today at 19:00 before anything was opened.

FED PATH resolved the countdown correctly — `Priced for the next decision
(TODAY, settles Wed 16 Sep) — Hike 25bps 86% · Fed maintains rate 12%` — and
the odds had moved from 80% on 13 Sep, so the figure is live rather than
carried. RISK WINDOWS listed all four components separately (19:00 projections,
statement and rate; 19:30 presser) rather than collapsing them into one line.

**And the ETF sign-flip flag fired correctly, on a real reversal:** `+175, -47,
-120, -283, -13, +160 — FLAG: sign flipped after 4 consecutive sessions of
outflow`. That detector is the one the synopsis records as having once been
inverted — counting the current streak instead of comparing against the prior
one, so it fired on steady runs and stayed silent on reversals. **This is the
first time in this run of sessions it has been observed firing on an actual
flip**, which is the case it was rewritten to catch.

Macro quotes were also `as of 09:10 LIS` — minutes old, against the 40-hour
stamps a weekend brief carries. The age-stamp machinery is doing what §2.3
recorded, in both directions.

The AHEAD countdown also reached **T-0 for the first time this session**: the
Canada tariff scope change, tracked since T-2, surfaced in Tuesday's subject
line as `TODAY Modifying the Scope of Produc…`. Partial evidence for §5's open
question about whether the radar surfaces anything useful — one landing is not
the month of observation that question asks for.

### §2.1g The weekend guard, caught in the act — 2026-09-13

The Triggers page settles two things at once, and the second was not expected.

| Column | Value |
|---|---|
| Owner / Event / Function | Moi · Basé sur l'heure · `sendBrief` |
| Deployment | **Head** — runs the newest saved code, not a pinned version |
| Error rate | **0%** |
| Last run | **13 Sep 2026, 09:20:11** |

**The timer fired this morning at 09:20:11, did not error, and no brief
exists.** GitHub logged no run at 08:20Z; Gmail holds nothing before the manual
13:38 dispatch. A trigger that ran, returned cleanly, and produced nothing is
the weekend guard, executing exactly as the old code was written to.

✅ CONFIRMED — and this is an upgrade in evidence, not a new finding. Until now
the stale-copy diagnosis rested on inference: weekdays worked, weekends did
not, and the guard was visible in the old source. **It is now observed
directly**, from the one surface that had never been looked at. §3.16's claim
that "every guard watches for failure, none watched for absence" has its
sharpest possible illustration: Google's own dashboard rendered this morning's
lost brief as **0% error**.

**The lesson for the register:** a green health indicator on a component that
did nothing is not evidence the component worked. `0%` here means "nothing
threw", which is a different statement from "the brief was sent" — the same
gap between *ran* and *delivered* that put a false ✅ in §2.1d.

### §2.1f Trigger v7 live — 2026-09-13

| Fact | Evidence |
|---|---|
| Google runs the new code | Apps Script log `Brief dispatched 16:26 LIS (trigger v7).` — the `(trigger v7)` suffix exists only in the new file |
| GitHub received it | run #64, `2026-09-13T15:26:45Z`, `workflow_dispatch`, success — 16:26 Lisbon, the same minute |
| The version handshake passes | delivered brief goes straight from `built 16:26 LIS` to `## THE SETUP`; no `TRIGGER OUT OF DATE` banner, where run #61 with `trigger_version=6` printed one |
| Delivery | 15:27:01Z, ~16 seconds after dispatch |
| The honest delta label, in a real email | `BTC $77139, +0.5% vs earlier today` — the second brief of the day, correctly not called "vs yesterday" |

✅ CONFIRMED end to end, and the detector's negative case is now confirmed too:
it stayed silent when the versions agreed. A warning that only ever fires is
worth nothing; this is the first evidence it does not.

**Still unverified:** the daily timer itself. `testNow` exercises the code
path, not the schedule. See §5.

### §2.1e The weekend gap, and why nothing raised it

| Link in the chain | What it did on Sat 12 Sep | Why it stayed silent |
|---|---|---|
| Apps Script `sendBrief` (Google copy) | ran, hit the weekend guard, exited | it did not throw, and Google only emails on a throw |
| GitHub Actions | nothing | a run nobody requests is not a failed run |
| The workflow's own crons | nothing | they were still `* * 1-5` in the last run's checkout |
| The test suite | green | it tests the brief, and the brief was never built |
| `state/latest.json` | held `2026-09-11` | nothing had ever compared it to today |
| §2.1d, this file | recorded ✅ | written from the intent, not from the inbox |

✅ CONFIRMED. **Six places could have noticed and none was looking**, because
every one of them watches for a failure and this was an absence. That is the
finding, and §3.16 states it as a rule.

### §2.6 D21 proven in production on the PM edition's first render — 2026-09-18

Run #87, `BRIEF_EDITION=pm`, `skip_email`. The state file on the branch
predates the bundle, so it carries no `am` key — which is exactly the
condition D21 exists for, arriving by accident on the first live run.

```
# PM DELTA — Friday, 18 September 2026
*Pre-NY-open scan — built 23:40 LIS.*

## SINCE 09:20
- **BTC** $81,162.90 · no morning baseline, so no delta
- **ETH** $2,621.52 · no morning baseline, so no delta
- DXY 100.22 (+0.76%) · US 10Y 5.00 (+0.75%) · S&P 500 fut 7,725.00 (+1.31%) …

> **⚠ No 09:20 brief was recorded today, so every delta above is suppressed
> rather than measured against yesterday. …**

## MATERIAL CHANGE
- No material change since 09:20.
```

**It suppressed rather than substituted.** The obvious wrong behaviour — fall
back to the previous *day's* close — would have printed a plausible percentage
measuring the wrong interval. That is §3.18 exactly, the bug that cost a
correction in rev 7. The edition printed absolute levels instead, said why,
and banner-flagged it.

Also confirmed in the same run: `No state change to commit.` The PM touched
nothing.

### §2.5 The latency banner, proven on a runner — 2026-09-18


Built, then fired deliberately rather than waited for. A dispatch at 12:56
Lisbon carrying `trigger_version: 7` and `skip_email: true` is 3h31m past the
09:25 target, so the check had to fire — and it did, in both places it should.

**Actions annotation (run #78, job 105590008204):**

```
##[warning]BRIEF LATE — built 12:56 Lisbon, 3h31m past the 09:25 target.
The external trigger dispatched late, unless this brief was pulled by hand.
```

**And in the brief itself**, under the build stamp and above THE SETUP:

```
*Cloud run — built 12:56 LIS.*

> **⚠ BRIEF LATE — built 12:56 Lisbon, 3h31m past the 09:25 target. The
> external trigger dispatched late, unless this brief was pulled by hand.**
```

Three things this run establishes beyond the banner:

- **The wording is the dispatch one, not the fallback one.** `BRIEF_SCHEDULE`
  was empty and `TRIGGER_VERSION` was `7`, which is exactly the ambiguous case
  — and the note says *"unless this brief was pulled by hand"* rather than
  accusing a working trigger. It was, in fact, pulled by hand.
- **`skip_email` left the state file untouched** (`No state change to
  commit.`), so proving the detector cost nothing: no email, no baseline
  shift, no `last_sent_date` write.
- **The self-test gate passed on the runner** before the build, so the 26 new
  checks run in CI and not only on a laptop.

> ⚠ **What this run does NOT establish.** The fallback wording — the one that
> matters on 7 November — has never been produced by a real cron run. It is
> covered by four offline tests, and offline is not a runner (§8). The first
> genuine proof will be the first morning the trigger fails, which is by
> construction not schedulable. Recorded as evidence-pending rather than
> silently counted as proven.

*Evidence: run #78 `workflow_dispatch` 2026-09-18 11:56:07Z, conclusion
success, log lines 11:56:32.986 and 11:56:32.987.*

### §2.2 Token permission for the external trigger — measured, not assumed

`.github/workflows/probe-permissions.yml`, run 33981684155, three jobs:

| GITHUB_TOKEN permission | Result |
|---|---|
| none | `403` · `x-accepted-github-permissions: actions=write` |
| `Actions: write` | `204` — accepted |
| `Contents: write` | `403` · `x-accepted-github-permissions: actions=write` |

✅ CONFIRMED. The dispatch endpoint wants `Actions: write` **and nothing else**,
and `Contents: write` is refused. See §4 for the retraction this forced.

### §2.3 Live section verification (run 34032*, 2026-09-06)

| Section | Live evidence |
|---|---|
| AHEAD | `T-89 · Fri 04 Dec — Adjusting Imports of Polysilicon…· effective` — a tariff date extracted from proclamation prose, where the structured field is null |
| POLICY DESK | `Warsh 28 Aug · In Our Time · speech`; `Buyback 03 Sep · $12.5bn accepted of $28.3bn offered · 1Mo to 2Y` |
| FLOWS | `BTC ETF 04 Sep: +$174.6m · 6-day run: -202, +217, -236, +101, +731, +175` |
| DERIVATIVES | `BTC perp funding +0.0000%/8h · OI 847,712,190 · Deribit (single venue)` |
| State/deltas | `ETH $2,504.01 · +1.5% vs yesterday` |
| Stale-quote honesty | `DXY 99.16 (as of Fri 04 Sep 21:59 LIS — 39h old)` |

### §2.4 Test coverage

✅ CONFIRMED: 710 lines, offline, no network, run as a gating step before every
brief. Covers ET→Lisbon across both DST-mismatch windows, feed parsing and
dedupe, max pain, monthly expiry detection, ETF flow-run sign flips, the cron
slot guard in both seasons, stale-quote age stamps, risk-window filtering,
weekends, the state file, watchlist parsing, prose date extraction, the
two-tier relevance filter, CDATA/BOM feed parsing, and POLICY DESK rendering in
healthy / quiet / failed states.

---

## §3 · THE FINDINGS

**§3.1 — GitHub's scheduler is not a scheduler.** `on: schedule` is documented
best-effort and is deprioritised for low-activity repositories. 12/12 late.
*Evidence: §2.1.*

**§3.2 — A manual dispatch is instant.** Every `workflow_dispatch` this session
started within seconds. The mechanism for on-time delivery already exists and
is already wired; only the external caller is missing. *Evidence: ~10 dispatches
this session, all sub-minute.*

**§3.3 — The trigger token is cheap, contrary to what was claimed.** It needs
`Actions: write` on one repository. That cannot push code, edit a workflow, or
read a secret. *Evidence: §2.2.*

**§3.4 — Structured fields lie by omission.** The Federal Register publishes an
`effective_on` column and populates it for 0 of 21 presidential documents. The
dates that move markets are in the prose. *Evidence: probe round 5.*

**§3.5 — But the prose is boilerplate, so it is extractable.** "goods entered
for consumption, or withdrawn from warehouse for consumption, on or after 12:01
a.m. eastern time on August 19, 2026" recurs almost verbatim across
proclamations. Requiring a cue phrase **and** a future date removes citations to
prior orders, because those all point backwards. *Evidence: probe round 6;
live-verified §2.3.*

**§3.6 — Substring matching put junk in a real brief.** "trade" matched
"Trademark"; "oil" matched a marine-mammal permit; "export" matched a customs
filing upgrade. Fixed with word boundaries and a two-tier word list, and all
three are now regression tests. *Evidence: live brief 2026-09-05, run
33986074445.*

**§3.7 — A feed answering 200 is not a feed carrying signal.**
`home.treasury.gov/rss.xml` returns 200 and contains careers pages and SSBCI
FAQs. *Evidence: probe round 8.*

**§3.8 — The probe-first discipline works, and it is the asset here.** Nine
rounds, and every single one changed a design decision rather than confirming
one. Sources wired without a probe (Farside, Binance, the next-week calendar)
are exactly the ones that failed in production. *Evidence: §12.2.*

**§3.9 — A section can fail by formatting, not only by omission.** Kabil
reported the brief said nothing about Treasury tripling long-end buybacks to
$6bn. It had. The line was
`Buyback 10 Sep · — accepted of — offered · 10Y to 20Y · settled 11 Sep`:
the correct operation, on the correct date, typeset exactly like a finished
one under blank amounts, reading as broken data rather than as the day's most
consequential event. **Present-but-unreadable is a failure mode, and no test
that checks "is the number there" will ever catch it.** *Evidence: run
102797967158, 2026-09-10.*

**§3.10 — Fiscal Data returns the STRING `"null"`, not JSON null.** Every
comparison against `None` sees a truthy string and proceeds. This is the
mechanism behind §3.9 — an operation with no result yet was never recognised
as one that had not run. *Evidence: same run; `_fd_val` and its tests.*

**§3.11 — Three tests can be green while the fetcher does not exist.** The
suite fed `render.build` fixtures and never called `treasury_ops`, so deleting
a helper it depended on produced a fully green run and a live
`NameError`. Fetchers now get an offline end-to-end test with `_json` stubbed.
*Evidence: run 102862384592 — "Treasury operations unavailable — buybacks:
NameError; auctions: NameError", suite green.*

**§3.12 — A true statistic about the wrong population is a wrong number.**
The first fix printed "1.5× the recent norm of $4.0bn" for the $6bn
announcement, because the median mixed long-end operations ($2bn caps) with
short-end liquidity operations ($12.5bn caps). Arithmetically correct,
materially false: it reported a tripling as a 50% bump. Norms are now computed
within a maturity bucket and refused entirely below two same-bucket peers.
*Evidence: dry-runs 102863173257 (wrong) → 102864401381 (`3.0× the $2.0bn norm
for this maturity bucket`).*

**§3.13 — GitHub's own token UI has two silent traps.** Both cost hours.
(a) Setting **Expiration to "Custom"** with a typed date makes *Generate token*
do nothing at all — the rejection renders at the top of the form, off-screen for
anyone scrolled to the button. Switching to a preset (60/90 days) generates
immediately. (b) When the form rebuilds after that change, the **Actions
permission is silently dropped**, producing a token that reads fine and cannot
dispatch. *Evidence: four failed attempts 2026-09-07→08; the second trap was
caught only because the token was tested with a real dispatch call before the
Google setup began.* **Test a credential before building on it.**

**§3.39 — Cadence was the right metric, and it nearly handed me a worse feed
than the one it rejected.** Rounds 21 and 22, 2026-09-20, after Kabil asked
whether the brief watches his four X accounts. It watched one, through its
website.

X costs $0.005/read with no free tier and Nitter is under cease-and-desist, so
round 21 probed twelve free primaries. **The measure that decided it was
cadence — items per hour — which round 14 never took.** The AM edition looks
back eighteen hours and almost anything fills it; the PM edition looks back
about three and a half, and a feed under ~1 item/hour is empty most
afternoons. *An empty section that is empty by construction reads as "nothing
happened", in the one part of the brief carrying no numbers to contradict it.*

Round 21's winner was Reuters via Google News at **4.3/h**, roughly nine times
everything else. **The first live PM edition printed:**

```
Pirates' Brandon Lowe takes HR barrage into finale vs. Royals - Reuters
Olympic dreams flicker as teqball awards first Asian Games medals
```

**A title deny-list does not fix that** — those contain no sports word any
filter would catch. Reuters files sport under `/sports`, so the scope belongs
in the query: structural, not a guess about what a headline is *about*, which
is the only kind of filter §3.6 trusts after `trade` ⊂ `Trademark`.

**Round 22 then found a worse trap than the one it went looking for:**

| scope | cadence | what it actually returns |
|---|---|---|
| unscoped | 4.3/h | baseball |
| `/markets` | **4.7/h** | **`1928.SG — Stock Price & Latest News`** — quote pages |
| `/markets+/business` | 4.7/h | same |
| `/business` | 0.9/h | clean, too thin for the PM window |
| **`/markets+/business+/world`** | **4.2/h** | Bessent–China, China LPR, TotalEnergies |

`/markets` returns Reuters **ticker landing pages** at nearly five an hour, and
**cadence alone rates it the best feed of the five.** A metric that was right
about the first problem was one step from handing over a worse one. That is
why the probe prints sample titles and says to read them, and why the round
that follows a successful metric is the dangerous one.

Shipped: the three-section scope, plus a **structural** filter for the quote
pages — Reuters' own page-title template and a bare exchange-suffixed ticker,
both anchored so `SAP.DE beats estimates as cloud revenue climbs` survives. *A
ticker inside a sentence is a story; a ticker that **is** the sentence is a
landing page.*

**Open, and Kabil's call.** `/world` is what carries the geopolitics — and it
also carried *"Diana's brother compares media treatment of Harry, Meghan"* and
*"Billionaires abound in California. Why not tax their wealth?"*. Dropping it
costs the macro geopolitics and takes cadence to 0.9/h. There is no structural
answer left: the remaining choice is taste.

**§3.38 — The brief printed US bank reserves as three quadrillion dollars,
every morning.** Found by reading run #103 — the real, emailed Sunday brief —
rather than by any test. Probe round 20 settled it the same day.

```
- **Treasury account** $877,028bn        ← $877 trillion
- **Bank reserves**  $3,013,794bn        ← $3 quadrillion
```

Bank reserves are about **$3.0 trillion**. Probe round 20 asked FRED what it
actually returns:

| series | brief said | FRED says | |
|---|---|---|---|
| `RRPONTSYD` | `$bn` | Bil. of US $ | ✅ |
| `WTREGEN` | `$bn` | **Mil. of U.S. $** | ❌ 1000× |
| `WRESBAL` | `$bn` | **Mil. of U.S. $** | ❌ 1000× |

**Two layers asserted the scale and neither checked it.** `PLUMBING_SERIES`
carried a `unit` field — and `_plumbing_lines` ignored it and hardcoded `"bn"`
anyway. Either alone is a guess; together they are a guess that *looks* like it
was considered twice. §3.9 for the sixth time.

**The unit column was deleted rather than corrected.** Writing the right answer
into the table is still a declaration, and the next series added would be
another coin flip. `plumbing()` now asks FRED what the series is measured in
and scales from that; the renderer prints the unit it is handed.

An unrecognised unit is not a licence to guess: the value prints unscaled
carrying FRED's own words, and a failed lookup degrades to `unit unknown` with
the reason in `partial`. **Better an unlabelled figure than a confident wrong
label** (§12.4a). Cost is three extra calls to a host the morning brief already
uses; the PM edition pays nothing since §3.36.

> **The old test was green and would have rendered `$3,120$bn`.** The fixture
> said `"unit": "$bn"` while the renderer hardcoded `"bn"` — and no assertion
> ever looked at the unit. The third test in three days that passed while
> describing something that did not happen.

*Verified live on run #105: `$877bn` and `$3,014bn`.*

**§3.37 — The shadow log was recording test dispatches as if they were
editions.** Found while verifying §3.36 on a runner, 2026-09-19.

`SKIP_EMAIL` returns from `main()` **before** the state write, so a test
dispatch never touches `latest.json` — which is why the morning verification
run was safe and needed no restore. But `write_shadow()` runs **before** that
return, so every `skip_email` dispatch appended a row to the D20 log.

Three were already in the file, from dispatches at **14:30, 15:25 and 15:38**
Lisbon. None is a 13:00 edition. The thresholds are being calibrated on the
**09:20-to-13:00 window**, and a 15:38 sample measures six hours where the row
claims four.

**§3.35's lesson, met a second time within the hour: a wrong banner gets seen
and fixed; a wrong dataset gets averaged.** The file is the only evidence that
will ever exist for setting v2's thresholds, and half its rows were measuring
an interval nobody asked about.

Gated on `sending`. Rows deleted; the file is empty again, which is honest.

**The test for it is driven through `main()`, not by reading the source for an
`if`.** The first version asserted the string `if sending:` appeared in the
right place — which is §3.33's exact shape, a test staying green because a line
is present while the line does nothing. It now runs `main()` end to end against
a temporary shadow path with `SKIP_EMAIL` on and off, and checks whether a row
actually appears. The suite stays offline and finishes in 0.25s.

**§3.35 — The PM edition announced Friday's session as today's, and quietly
poisoned the dataset meant to calibrate it.** Found on run #95, 2026-09-19.

The body printed, at 14:20 on a **Saturday**:

```
**DXY +0.76%** on the session
```

The cash and futures markets were shut. That was **Friday's** session. The
spine carried the same number as a bare percentage with no date — and a bare
percentage is character-for-character what today's move looks like.

**The timestamp was on the payload the whole time.** `_yahoo_quote` has always
returned `as_of` from `meta.regularMarketTime`, and the morning brief has
always put every quote through `_as_of_stamp`, whose docstring argues this
exact case in full. **The PM edition simply never read the field.** Confirmed
on run #96: with the fix in, all four quotes print `(Fri 18 Sep)`.

**That is §3.9 for the fifth time** — present, sourced, and materially
misleading — after a buyback, a policy rate, a news headline and a section
heading.

**The third consequence was the one nobody would have seen.** `shadow.jsonl`'s
first and only row recorded `dxy 0.7591` and `us10y_bp 3.73` as
Saturday-afternoon PM moves. That file is the **entire** evidence base for
replacing v1's fixed thresholds with range-scaled ones (D20), and two of its
seven fields were measuring the wrong day before it had a second row. A
mislabelled banner gets noticed; a mislabelled dataset gets *averaged*.

**Fixed three ways, because a label alone was not enough:**

| Layer | Was | Now |
|---|---|---|
| Spine | bare `%` | dated: `(Fri 18 Sep)`, plus one line saying why |
| Body | fired on any quote | **freshness is a gate** — a stale quote fires nothing |
| Shadow log | stale value recorded as a move | **`null`**, so the gap is visible |

`null` rather than a dropped key on purpose: a missing key reads as *"the
dollar did not move"*, and the truth is *"the dollar was not trading"*. Those
are different claims and only one of them is true.

**No timestamp counts as not fresh** — §12.4a, absence of evidence is not
evidence. The spine prints `(no timestamp)` so a quiet body always carries a
visible reason rather than going silent, which is how this project's failures
prefer to arrive. *Evidence: run #95 log 13:20:21Z (the bug), run #96 log
13:31:17Z (the fix).*

**§3.34 — `BRIEF LATE` would have fired on every PM edition, for ever, and
retired the detector before it ever caught anything.** Found on run #95.

```
BRIEF LATE — built 14:20 Lisbon, 4h55m past the 09:25 target
```

**09:25 is the morning target.** `latency_note` had never heard of a second
edition, so it judged every PM brief against the morning clock. The PM edition
is built at **13:00 Lisbon by design** — 3h35m past 09:25, and seven times the
30-minute threshold. Every PM edition, every day, would have opened with a red
banner saying it was late while being exactly on time.

**Why this is worse than a cosmetic fault.** §5 and the `LATE_AFTER_MINUTES`
comment both say a detector that cries wolf gets retired inside a week. This
one would have cried wolf on **half of all briefs**. The check built after the
12 September gap — the one whose whole purpose is to catch a silent slide back
to a 4.5-hour delay — would have been trained into background noise before it
caught anything real.

**The target is anchored to New York, not to a Lisbon hour.** Same reason the
cron has two slots and the Apps Script has a New York guard: the Lisbon-NY gap
is 4, 5 or 6 hours depending on the week, so a hardcoded 13:00 would itself
have fired a false banner for an hour a day through **both DST mismatch
windows**. Verified across 400 consecutive days that the target lands on 08:00
New York on every one of them. *Evidence: run #95 (the false banner), run #96
— `1h30m past the 13:00 target`, correct for a 14:30 hand-pulled run.*

**§3.33 — The PM cron fallback was dead on arrival, and the test asserted the
config line's presence rather than its behaviour.** Found on run #92, the
first real firing of the `0 12` slot, 12:34 UTC:

```
BRIEF_EDITION:
A brief for 2026-09-19 was already sent; this scheduled run is a duplicate.
```

The YAML `${{ }}` expression that resolved the edition from the cron produced
an **empty string** on a scheduled run. So the PM slot ran the *morning* path,
hit the morning's duplicate guard — which was true, the morning brief had gone
out — and exited in **zero seconds reporting success**. The entire afternoon
fallback was inert, and nothing would ever have looked broken.

**The comment directly above that expression described this exact failure. The
comment was right and the code was wrong.**

**The test is the part worth keeping.** It asserted the workflow file
*contained* the expression. It was green from the moment it was written,
because the string was there and the string did nothing. **A test on a config
line's presence is not a test on its behaviour**, and this one bought false
confidence in precisely the place that could not otherwise be seen.

Resolution moved into `main.edition()` for one reason: Python can be tested and
a `${{ }}` expression cannot. `PM_CRON_SLOTS` is declared rather than derived
from the New York hour, because which slot lands on 08:00 NY changes with US
daylight saving and **both** must resolve to the PM edition — so
`should_run_pm` is what rejects the non-owner, with its own message, rather
than the morning guard rejecting it with a misleading one about a duplicate.
*Evidence: run #92 log, 12:34:44Z.*

**§3.32 — "Still ahead today" printed tomorrow's entry, and the shape is the
one this file keeps meeting.** Found on run #87, one commit after shipping.

`_risk_windows` appends untimed radar entries at the **end** of its list, and
those open with `**Tomorrow**`. The PM spine selected windows by matching a
leading `**`, so at 23:40 — when no timed window remained — it fell through to
the first untimed entry and printed **tomorrow's** FRED maintenance under a
heading that says *today*.

Nothing was fabricated. The item was real, correctly dated and correctly
described. It was under the wrong heading. **That is §3.9 for the fourth
time — present, sourced, correctly stamped, materially misleading** — after a
buyback, a policy rate and a news headline.

The fix selects on a clock rather than on bold, and the empty case says
*"nothing further scheduled"* rather than leaving a heading that implies the
day is clear. *Evidence: run #87 log, 22:40:38Z.*

**§3.31 — The "no free liquidation source" verdict was wrong, and it was
wrong in exactly the shape this file has a section about.** Probe round 18,
target 1:

```
https://www.okx.com/api/v5/public/liquidation-orders
HTTP 200 · 767 bytes · application/json   ← no key, no signup
{"code":"0","data":[{"details":[
  {"posSide":"short","side":"buy","sz":"9.4",  "bkPx":"81347.5","ts":"1789758976511"},
  {"posSide":"short","side":"buy","sz":"146.2","bkPx":"81224.6","ts":"1789758961329"},
  ...], "totalLoss":..., "instId":..., "uly":...}]}
```

Every field the claim needs is there: **a size (`sz`), a timestamp (`ts`), and
which side was liquidated (`posSide`)**. The round's pass test was deliberately
strict — *a 200 is not enough* — and this clears it.

**§12.2 has carried `CoinGlass · S2 · no free tier, $29/mo` since rev 1**, and
§12.4a is the section about precisely this mistake: **CoinGlass being paid is
a property of that route, not a property of the world.** The register itself
marked the verdict *"unconfirmed rather than settled"*. It took one call to
settle it the other way.

**Why this one matters more than the other seven.** Kabil's own framework
opens with *"liquidation cascades, not support/resistance magic"*, and the
brief has never carried a single liquidation figure — not the level, not the
24h total, not the clusters. `docs/BUILD_PLAN_ADDENDUM_1.md` §6 calls it *"the
largest single gap between the stated framework and the system"*. That gap is
now a wiring job rather than a paid subscription.

**What it does not yet establish.** One call returned five rows of a single
`uly`. Nobody has checked the window it reaches back over, whether an
aggregate 24h total is derivable without paging, or how it behaves on a quiet
day. That is round 19's work, and none of it is wired.

**§3.30 — The first live NEWS run proved D16's marking necessary within
three headlines.** ZeroHedge was admitted (D16) as commentary *on the
condition that it is visibly marked*, because §12.8 warned it *"mixes market
stories with political commentary"* and an opinion typeset like a fetched
number is §3.9 inverted.

Run #86, the first live render, returned exactly that mix:

```
- **2h ago** — The Pathocracy Of Women In The Democratic Party
  · **ZeroHedge — commentary, not a wire**
- **2h ago** — Midwest Braces For Diesel Crisis After Exxon's Joliet
  Refinery Suffers Disruption · **ZeroHedge — commentary, not a wire**
- **3h ago** — US Drops Venezuela From List Of Countries Failing To
  Combat Drug-Trafficking · **ZeroHedge — commentary, not a wire**
```

**The marking works.** It is bold, it is adjacent, and no reader would mistake
those lines for the wire.

**And one of the three is a culture-war headline with no market content at
all.** The second is a genuine refinery-disruption story and the third is a
sanctions-adjacent one; the first is noise in a document where every other
line is a fetched number.

So the marking is doing its job and the signal-to-noise is still poor. That is
**a decision for Kabil, not a bug to fix**: D16 is his, taken with the warning
in front of him. The options, in the order I would take them: keep it and
accept a third of the slot being noise; **filter it with §3.6's two-tier word
list**, the same machinery that stopped `trade` matching `Trademark`; or drop
it and let CNBC carry the section alone. Recorded so the choice is made on
evidence rather than on the memory of a probe. *Evidence: run #86,
2026-09-18 22:23:07Z.*

**§3.29 — The offline test suite was not offline, and had been opening a
real connection to Gmail on every run.** Found 2026-09-18 while wondering why
the suite had started timing out locally at 170 seconds when the same suite
finishes in two on a runner.

`tests/test_brief.py` opens with *"No network. Everything here must pass
before the workflow is trusted."* One test called `main.send_email()` with a
deliberately fake App Password to check that a **spaced** password is not
mistaken for a missing one. `send_email` opens `SMTP_SSL("smtp.gmail.com",
465)` and calls `login()`. So the check passed by **making a real connection
and a real failed authentication attempt against Kabil's account**, every CI
run, from a shared GitHub runner address.

Two costs, and the second is the one that matters:

1. **Speed.** Wherever SMTP is blocked the connection hangs to its 60-second
   timeout. That is the entire reason the suite was slow — with the call
   removed it runs in **0.17 seconds**, from over 170.
2. **Repeated failed auth from CI is how an account gets throttled.** Nothing
   had gone wrong yet. It was a live risk sitting inside the gate that
   protects every send.

The fix is a split, not a mock: `main.credentials()` now owns the validation
and `send_email` calls it. The test calls `credentials()` and never touches a
socket.

**The general form.** A test suite that promises no network and makes a
network call is a **gate reporting a property it does not have** — the same
shape as §3.24's docstring, which claimed the target range was the decision
itself. Both were true of the intent and false of the code. *Evidence: suite
runtime 170s+ → 0.17s with the call removed; `main.send_email` opened
`SMTP_SSL` before this change.*

**§3.28 — Yahoo rate-limits an Actions runner, and thirteen live lines sit on
it.** Probe round 17 asked Yahoo for IBIT and for Brent. Both returned
**`HTTP 429 · 19 bytes · Too Many Requests`** — not a block, a rate limit, and
the first of the two calls got it as readily as the second, so it was not
self-inflicted by probing twice.

**This is not a verdict on IBIT or Brent.** Neither was tested; the host never
answered. Recorded as **inconclusive**, because "I could not reach it once" is
not "it does not work" — the mistake §12.4a cost two wrong verdicts to learn.

> ⚠ **CORRECTED 2026-09-18 by round 18 — and the correction is mine.** Round
> 18 re-probed all three symbols on `query2` and drew `429` again. Same
> result, different host — which looks like confirmation until you notice
> that **the brief's own Yahoo calls succeeded in runs #82, #83, #84 and #86,
> minutes either side of both probes.** Seven symbols, no failures.
>
> The difference is not the host and is probably not the runner. It is the
> headers: `sources.py` sends `{"User-Agent": UA, "Accept": "*/*"}`, and both
> probe rounds sent a **browser-shaped** User-Agent with a JSON `Accept`.
> A browser fingerprint on an API endpoint is a normal thing to rate-limit.
>
> So the conclusion below is **overstated**. What is established: *this
> probe's client* draws a 429 from Yahoo. What is **not** established: that
> Yahoo rate-limits the brief. Round 19 repeats the call with
> `sources.HEADERS` and settles it. IBIT and Brent remain untested either way.

**What it MAY be a verdict on is the host — pending the correction above.**
Yahoo already carries DXY, 10Y, gold,
WTI, VIX, S&P futures, Nasdaq futures, Nikkei, Hang Seng, USDJPY and CNH —
eleven shipping lines, thirteen once IBIT and Brent land, **with no fallback on
any of them.** The 09:20 brief has never seen a 429, but nothing about 08:20
UTC is privileged; Actions runners share IP space and this probe drew a 429 at
11:59 UTC from the same platform.

`§12.5`'s kill criterion watches individual sources going quiet. **It does not
watch a host becoming load-bearing**, which the build plan flagged as a
theoretical risk on 17 September and this probe turned into a measured one the
next day. Logged, not fixed: a fallback for eleven lines is a project, not a
commit. *Evidence: probe run #17, job 105590900580, targets 6 and 7.*

**§3.27 — A well-formed 200 answered a different question than the one asked.**
Target 4 called Polymarket's gamma API with `closed=false` and `tag=fed`,
looking for the next FOMC market **without a date in the query** — because a
query carrying a month is a query that silently goes stale.

It returned `HTTP 200`, valid JSON, five markets. The first was **"Will Adanech
Abiebie be the next Prime Minister of Ethiopia?"**, `endDate`
`2026-06-01` — an Ethiopian election market that closed three and a half months
before the call.

Two filters failed silently and neither said so:

| Asked | Got |
|---|---|
| `tag=fed` | markets with no relation to the Fed — the tag was ignored |
| `closed=false` | a market whose `endDate` had already passed |

**Nothing about the response announces either failure.** Status 200, correct
content type, well-formed objects, populated fields. A fetcher written against
this would have printed a foreign election's odds under a heading reading
*"Priced for the next decision"* — §3.10's exact shape, and worse than a 404,
which at least fails loudly.

**Verdict: Polymarket stays unwired, and the bar for wiring it has gone up.**
It would now need a probe proving a filter is *honoured*, not merely accepted.
And the argument for bothering is weak: **Kalshi is already LIVE, keyless, and
generalises by ticker** — it needed no probe because its tickers carry the
meeting, where Polymarket's slugs carry a month string. *Evidence: probe run
#17, target 4.*

**§3.26 — The token expiry has no detector, and the system would report
itself healthy all the way down.** Raised in the 2026-09-17 planning chat
(`docs/BUILD_PLAN.md` §5) and **verified against the code here before being
recorded.**

Walk the chain:

```
token expires 2026-11-07
  -> Apps Script dispatch returns 401, throws, Google emails Kabil   [caught]
  -> no workflow_dispatch run at 08:20Z, so no brief at 09:20        [NOT caught]
  -> the scheduled cron ("25 8" / "25 9") fires hours later          [by design]
  -> the brief DOES arrive, just four hours late
  -> state/latest.json gets last_sent_date = today
  -> health.py: no day was missed  -> delivery_note() stays silent
  -> health.py: the script version is fine -> trigger_note() stays silent
```

**Verified, not assumed:** `health.py`'s `notes()` calls exactly two checks —
`delivery_note()` (missed days) and `trigger_note()` (script version). Neither
looks at *when* the brief was built. The cron fallback is still registered at
`25 8` / `25 9` in `market-brief.yml`. So the chain holds: **the project would
silently return to the 4.5-hour delay it spent three weeks solving, with both
detectors green.**

This is §3.16 a second time, one level up. The first detector answered *"was a
brief sent?"* Nothing answers *"was it sent on time?"* — and on-time delivery
is the thing this project actually measures itself by (§9).

**The fix is small:** the brief compares its own build time against target and
banners past 30 minutes. It needs no new source, no probe and no schema change.

> ✅ **FIXED AND PROVEN LIVE, 2026-09-18 — rev 22.** `health.latency_note()`
> ships, 26 tests cover it including the rendered-brief path, and run #78 put
> the banner in front of a reader. §2.5 has the run. The fallback wording — the
> one the token expiry will actually produce — remains offline-tested only, and
> §2.5 says so rather than counting it.

**One claim in the same plan section does NOT hold, and is corrected here.**
The plan states that `muteHttpExceptions: true` makes a 401 *"return as an
ordinary response"* so *"Google sends no alert and the failure is completely
silent"*, and asks for a non-200 throw. `trigger/apps-script.gs:104-113`
already throws on `code !== 204`, with a comment giving that exact reason.
**The hole described is closed and has been since v5.** Recorded so nobody
spends a commit rebuilding it. *Evidence: `scripts/health.py` `notes()`;
`.github/workflows/market-brief.yml:17-19`; `trigger/apps-script.gs:104`.*

**§3.25 — A scheduled task with the ability to send mail has been firing
daily outside this repository, and nothing in this file knew it existed.**
Found 2026-09-18, while checking that no check-in was armed to fire into a chat
about to be closed.

What is there, read from the Routines listing itself:

| | |
|---|---|
| id | `trig_01T37HzNWDCP9qTWkrEgANre` |
| name | *Market Brief 09:45 LIS — WET slot (winter)* |
| schedule | `45 9 * * 1-5` — **UTC**, weekdays |
| created | 2026-08-21 · last edited 2026-09-05 |
| state | **enabled** |
| last run | 2026-09-17 09:45:54Z → finished 09:46:08Z, SUCCEEDED |

It carries the v4 chat-era prompt. **MODE A** relays the cloud brief out of
Gmail into a chat and sends nothing. **MODE B** fires when no cloud brief is
found: it builds a degraded, search-sourced brief and **emails it to
`kabil.dh@gmail.com`** with `(local build)` in the subject.

Three things follow, and only the first is comfortable.

1. **It has never produced a brief.** Fourteen seconds from fire to finish is
   the slot guard exiting, not a build. Lisbon has been on WEST (UTC+1) for
   every day of this project's measured life, and the guard exits on WEST.
2. **It is harmless by accident, not by design. Lisbon returns to WET on
   Sunday 2026-10-25.** From Monday 26 October the guard stops exiting and the
   task runs for real, weekdays at 09:45 Lisbon — 25 minutes after the cloud
   brief lands. **28 October, the next FOMC and §3.24's next occurrence, falls
   inside that window.**
3. **Its own premise is false.** The prompt states *"two tasks are registered
   and exactly one owns today."* A full listing — `include_completed: true`,
   disabled and already-fired Routines included — returns **one**. The summer
   (WEST) slot does not exist. The pair that made the guard safe is half
   missing, and the half that survived is the half that wakes up.

The general form is the part worth keeping. `health.py` detects a brief that
did not arrive. **Nothing detects a second sender that did** — a `(local
build)` email lands in the same inbox, under a similar subject, built to a
standard this file has never reviewed, and no check in this repository would
ever see it. *Evidence: Routines listing 2026-09-18 with `include_completed:
true`, one enabled entry; its `last_run` SUCCEEDED in 14s; tz database
Europe/Lisbon, WEST→WET 2026-10-25.*

**§3.24 — The brief carried a superseded policy rate for two mornings, and
its own docstring claimed it could not.** The FOMC raised the target range to
**3.75–4.00% on 16 September**. On the 17th and again on the 18th, FED PATH
printed `Target 3.50–3.75% · EFFR 3.63% · as of 16 Sep`.

The mechanism: `policy_rate()` reads `targetRateFrom`/`targetRateTo` off the
**EFFR row** of the New York Fed's `latest.json`, and the NY Fed publishes EFFR
one business day in arrears. So the target range inherits EFFR's publication
lag — **even though a target range is knowable the instant the statement drops,
and the brief already fetches that statement** (POLICY DESK carried
`FOMC 16 Sep · Federal Reserve issues FOMC statement` on both days).

The docstring asserts exactly the property the data does not have:

> *"Straight from the New York Fed's own rates endpoint, which is the desk that
> publishes the effective rate, **so this is the decision itself rather than a
> report of it**."*

It is not the decision. It is the range that was in force on the last day EFFR
was published, which trails the decision by one to two business days — **wrong
for a day or two after every FOMC, eight times a year, on precisely the
mornings the number matters most.** A reader seeing `Target 3.50–3.75%` on
Thursday would reasonably conclude the Fed had held.

Not a fabrication: the age stamp is honest and says `as of 16 Sep`. But the
stamp does not say *"this range predates a decision that has already
happened"*, and that is the whole difference. **§3.9 again — present, sourced,
correctly stamped, and materially misleading.** *Evidence: brief runs #74 and
#77; FOMC statement 2026-09-16; `sources.py` `policy_rate`.*

> ✅ **FIXED 2026-09-18 — rev 24.** The brief now cross-checks the range's
> `as_of` against the most recent **FOMC statement**, which POLICY DESK
> already fetches, so the check costs no request. A statement in that feed is
> evidence a decision *landed* — §3.23's distinction, which round 16 paid for.
> A scheduled watchlist date would not do: a meeting can move, and a statement
> cannot publish early. `as_of` **equal** to the decision date counts as
> stale, because the decision lands 19:00 Lisbon and the rate in force for
> almost all of that day is still the old one.
>
> **It flags; it does not fabricate.** The new range is in the statement prose
> and parsing that is separate work, so the marker sits beside the number and
> the note points at POLICY DESK where the statement already is. A test
> asserts the marker is within 60 characters of the range — §3.9's lesson,
> that a qualification the eye does not reach is not a qualification.
>
> ⚠ **Not yet seen firing in production.** By the time it shipped, the New
> York Fed had caught up: run #82 printed `Target 3.75–4.00% · EFFR 3.88% · as
> of 17 Sep`, which is correct and therefore silent. 17 offline tests cover
> it, including the rendered markdown and the HTML. **The first live proof is
> 28–29 October**, and recording that as pending rather than proven is the
> whole of §3.17.

**§3.23 — A calendar tells you what is planned; only the data tells you what
happened.** FRED's `releases/dates` returns the FOMC press release dated
26, 27, 28, 29, 30 and 31 December — every day to year end, for a release that
happens eight times a year. Those are projections, and the endpoint marks them
no differently from a release that actually landed. Round 15 saw one such date
and hesitated; round 16 asked for dates in the **future**, got 2,965 of them,
and settled it in a single call. **Publication must be proven from the data's
own vintage — the timestamp attached to the number — never from a schedule
that merely names the day.** The same shape as §3.17, where a change that had
been *made* was recorded as a change that *worked*. *Evidence: §12.10.*

**§3.22 — When two readings agree, the agreement carries no information.**
Round 15's decisive test fetched one payrolls figure two ways — as first
published and as it stands today — and got 159,075 both times. That result is
consistent with *"never revised"* and with *"the vintage lookup silently
ignored my parameters"*, and the values alone cannot separate them. What
separated them was a field nobody was comparing: `realtime_end: 9999-12-31` on
the initial release, meaning the first print is still current. **A test whose
pass and fail look identical is not a test** — design the check so the two
outcomes differ, or read the metadata that does. *Evidence: §12.9.*

**§3.20 — A mirror can lag the thing it mirrors by days, and the status code
says nothing about it.** `watcher.guru/news/feed` answered `200`,
`application/rss+xml`, 10 well-formed items, every one carrying a parseable
timestamp — and its **newest item was 41.9 hours old**, on a site whose X
account posts hourly. It also carried Tesla, Apple and Nvidia stories on a feed
meant to be the crypto beat. §3.7 said a 200 is not signal; this is the sharper
version — **the feed carried real signal, from the day before yesterday.**
Every freshness check in this project measures the *quote's* age; nothing
measured the *feed's*. A probe must read the newest item's timestamp, not just
count items. *Evidence: probe round 14.*

**§3.21 — A new fetcher on a host you already depend on can cost you the source
that works.** The Yahoo news feed answered `429 Too Many Requests` from the
runner. Yahoo's chart API is the entire MACRO & EQUITIES section. Wiring a
second, chattier call to the same host risks the rate limit landing on the
quotes instead — trading a section that works for one that might. **Before
adding a source, check whether its host is already carrying something you
cannot afford to lose.** *Evidence: probe round 14.*

**§3.19 — A green health indicator on a component that did nothing is not
evidence it worked.** Google's Triggers page showed `Taux d'erreur 0%` beside a
last run of `13 sept. 2026, 09:20:11` — the exact morning the brief did not
arrive. The figure was accurate: nothing threw. It was also worthless as a
delivery signal, because *ran without error* and *delivered* are different
claims, and only one of them is what anybody cares about. This is the same
confusion that put a false ✅ in §2.1d, arriving from the opposite direction —
there a change made was recorded as a change that worked; here a function
returning cleanly was displayed as a system functioning. **Before trusting any
dashboard, ask what it actually measures and whether that is the thing you
need.** *Evidence: §2.1g.*

**§3.16 — Every guard in this system watches for failure; none watched for
absence.** A throw is caught, a non-204 is caught, a degraded fetcher is
caught, a duplicate run is caught. A run that was never requested is not any of
those. On 12 Sep the trigger exited cleanly, GitHub was never called, and the
silence propagated through six independent checks (§2.1e) without tripping one.
**Absence needs its own detector, and the only place that can hold one is the
next thing that does succeed.** `scripts/health.py` compares `last_sent_date`
to today and the next brief names the days that never came. *Evidence: §2.1d,
§2.1e; run list for 12–13 Sep; Gmail.*

**§3.17 — The delivery record was written from intent, not observation — and
this file is where that error landed.** §2.1d recorded Sat 12 Sep as "09:20 LIS
✅". No brief existed. The row was written because the trigger had been changed
to run at weekends, and a change that was *made* was recorded as a change that
*worked*. **The project's single most important measurement had never once been
checked against the inbox**, which is the only place a delivery exists.
*Evidence: rev 6 wrote the row and its own "Requires Kabil" line predicted the
failure in the same commit.*

**§3.18 — A correct number under a confident wrong label.** Sunday's brief
printed `BTC $76,724, -0.6% vs yesterday`. The figure was right; the comparison
was against **Friday**, because `state.delta` compares against whatever the
state file holds and all three callers said "vs yesterday" regardless. One
missed brief silently turned every day-over-day line in the next one into a
two-day move wearing a one-day label. This is §3.12's shape again — a true
statistic described as something it is not — and it is the second time a
missing comparison population produced a wrong claim. The label is now derived
from the state file's own date. *Evidence: brief of 2026-09-13 13:38 LIS
against `state/latest.json` dated 2026-09-11; `render._vs_label` and its tests.*

**§3.14 — Positive: degradation is honest throughout.** Every fetcher raises
rather than returning a placeholder, every section prints `unavailable —
<reason>`, and an empty result is rendered differently from a failed fetch.
The brief has never printed a fabricated number. *Evidence: the "every source
down" test; the CoinGlass `0%` placeholder trap, avoided by quarantine.*

**§3.15 — Positive: Kabil rejects paid options consistently.** Zero-cost was
stated once and has held through every subsequent decision, including reverting
a working analysis layer at ~$4/month. *Evidence: sessions 5–6.*

---

## §4 · DECISIONS MADE

| # | Decision | Status |
|---|---|---|
| D1 | Recipient is a module constant, `kabil.dh@gmail.com`. No cc, no bcc, not overridable by env, input, or fetched content | ✅ Locked |
| D2 | Zero cost. A free tier behind a free API-key signup qualifies; a trial that converts to paid does not | ✅ Locked |
| D3 | No buy/sell calls, price targets, or position sizing anywhere in the brief | ✅ Locked |
| D4 | Every number comes from something fetched this run; unavailable is a correct outcome | ✅ Locked |
| D5 | Two cron slots (`25 8` / `25 9` UTC), job decides which owns today from the cron expression, not the wall clock | ✅ Locked |
| D14 | **Seven days a week** (was: weekdays only, `* * 1-5`, until 2026-09-12). Crypto, funding and OI do not stop at the weekend, and Monday's setup is built on it. Weekend briefs still suppress the cash-session windows and say the market is shut | ✅ Locked |
| D6 | Quarantine list — never fetch or cite: `deribit.com/statistics/*`, `optioncharts.io`, CME FedWatch, `coinglass.com`, `theblock.co/data`, `coinalyze.net` | ✅ Locked |
| D7 | Google Apps Script as the external trigger, not cron-job.org | ✅ **Locked — installed and proven 2026-09-08** (was: Accepted, not installed) |
| D8 | ~~The trigger token needs `Contents: write` and is therefore equivalent to the Gmail app password, so a third-party scheduler is unsafe~~ | ❌ **RETRACTED 2026-09-05.** Measured: the endpoint wants `Actions: write` and *refuses* `Contents: write` (§2.2). The claim came from community reports, not evidence. D7 still stands, but on convenience grounds — no new account — not security ones. cron-job.org was excluded on a false premise |
| D9 | No LLM analysis layer. Built, then reverted, to hold D2 | ✅ Accepted — consequence: the brief reports data, it does not interpret it |
| D10 | Curated watchlist is pipe-delimited plain text, not YAML — indentation must not be able to break it | ✅ Locked |
| D11 | Watchlist entries carry a last-confirmed date; >75 days prints as `unconfirmed` | ✅ Locked |
| D12 | Bessent tracked through operations (buybacks, auctions, refunding), not remarks, because Treasury publishes no usable feed — and the brief states the gap | ✅ Accepted |
| D16 | **ZeroHedge is IN, as visibly-marked commentary.** Own section, every line tagged `via ZeroHedge`, subtitle naming it commentary rather than a wire. This is the first non-fetched content the brief will carry, so the marking is the whole point: D4 guarantees every *number* is fetched, and anything that is not a number must be visibly not one. Dropped if it ever renders indistinguishably from a data line | ✅ Locked 2026-09-15 |
| D15 | **The brief monitors its own delivery.** `last_sent_date` is compared to today and any missed day leads the brief in red; the Apps Script reports `SCRIPT_VERSION` on dispatch and a mismatch with `scripts/health.py` is printed. Neither check ever guesses: no state date, or no version on the dispatch, produces no claim | ✅ Locked 2026-09-13 |
| D13 | ~~ETH ETF flows, aggregate liquidations **and Fed-path odds** stay out of scope. No free source~~ | ⚠ **PARTLY RETRACTED 2026-09-12.** Fed-path odds *are* freely available — Kalshi lists the decision as binary contracts over a keyless API (§12.2). The claim rested on CME's FedWatch being a data-free iframe, which was true and irrelevant: that is CME's *rendering* of the odds, not the odds. ETH ETF flows and aggregate liquidations still stand, but were reasoned the same way and are now **unconfirmed rather than settled** |

---

### §4.1 Decisions from the 2026-09-17 planning chat (D17–D24)

**Source and status.** Taken with Kabil in a planning chat on 2026-09-17,
recorded verbatim in `docs/BUILD_PLAN.md`. **None is implemented.** Evidence is
that document, not a runner — which under §12.3 makes every one of them a
design decision rather than a measured fact. They are binding on what gets
built; they prove nothing about what works.

| # | Decision |
|---|---|
| **D17** | **The PM edition is a delta, not a second brief.** Fixed spine (~6 lines) plus a body that prints only on material change; an empty body says `No material change since 09:20`. Daily, seven days a week |
| **D18** | **The PM anchors to New York, not Lisbon.** `atHour(8).nearMinute(0)` ≈ 07:45–08:15 ET, `atHour(7)` as documented fallback. Two Lisbon timers plus an NY-hour guard — the D5 two-slot pattern |
| **D19** | **Material-change thresholds are numeric and live in one config block.** v1 is fixed-percentage and regime-blind by acknowledged compromise; v2 is range-scaled, gated behind probe target 3 |
| **D20** | **The shadow log ships in the same commit as the PM edition.** Every run records what the body would have printed at every threshold, even when suppressed. Retrofitting discards the evidence that sets v2 |
| **D21** | **A missing AM baseline suppresses PM deltas entirely.** Absolute levels only, with the reason named. Never falls back to yesterday's close — that is §3.18 exactly |
| **D22** | **The brief never flags a level.** Proposed and rejected. Number, delta, age stamp. D3 and D9 stand unchanged |
| **D23** | **Policy scope is actions, scheduled announcements and dated plans — not remarks.** The wire is what catches an announced plan before it is signed |
| **D24** | **Stablecoins always print supply and dominance together, never dominance alone.** Dominance is a ratio: it rises when the denominator falls. Printing it alone hands Kabil a risk-off signal that is sometimes just a falling market wearing a costume |
| **D25** | **The weekend PM edition runs crypto only, and "shut" is decided by the quotes' own timestamps.** Kabil's call 2026-09-19 over skipping weekends. When every cross-asset quote is timestamped and every one is stale, the section is dropped and funding + liquidations take the slot — both 24/7. **A dead feed is never read as a shut market**: `failed` and `unknown` are separate states, because collapsing them would hide an outage behind a plausible story (§3.16) |

### §4.5 D25 — a detector may only claim what it can tell apart

**Locked 2026-09-18.** When two situations produce identical evidence, the
brief makes **one note naming both**, never one note picking the likelier.

The case that forced it: `testNow()` pulls a brief by hand through the same
`dispatch()` call, carrying the same `SCRIPT_VERSION`, as the timer. From the
runner's side a late dispatch and a hand-pulled brief are **the same bytes.**
The tempting fix was to infer from the size of the delay — hours means manual,
minutes means drift. That is a guess wearing a threshold, and §12.4a already
cost two wrong verdicts to learn what guesses cost.

So the fallback branch, which `should_run` genuinely proves, gets a flat claim
and names the token. The dispatch branch gets *"unless this brief was pulled by
hand."* One of those is an alarm; the other is a question. **Printing them in
the same words would have made both useless.**

The alternative — adding a `manual` flag to the Apps Script so the two really
could be told apart — was rejected for now: it bumps `SCRIPT_VERSION` to 8,
which makes every brief say `TRIGGER OUT OF DATE` until Kabil re-pastes. That
is real friction bought for a distinction he can make himself by remembering
whether he pressed the button. Revisit when the PM timer forces a bump anyway.

### §4.2 D11 amended — per-class confirmation horizons

**D11 is Locked, so this is an amendment and is logged as one.**

| Class | Horizon | Applies to |
|---|---|---|
| `policy` | **75 days** *(was: 75 days for everything)* | summits, OPEC, FOMC, announcements |
| `statutory` | **365 days** (new) | midterms and anything fixed in law |
| `holiday` | **365 days** (new) | US and China closures |
| `unlock` | **30 days** (new) | reserved — unlocks dropped, `docs/BUILD_PLAN.md` §11 |

**Reason:** a holiday entry would flag `unconfirmed` within 75 days of every
refresh, and **a flag that always fires is a flag nobody reads.** This is a
parameter on the existing mechanism, not a second mechanism.

### §4.3 D12 challenged and held

Bessent was raised in the same chat as a coverage gap. Under D23's scope he is
**not** one — buybacks, auctions and refunding are actions, and POLICY DESK
already carries them. **The flag was wrong and is recorded as wrong**, per §8's
own-errors-loudly rule. D12 unchanged.

### §4.4 The data-actuals PM edition is dead

**Reversed.** *(was, rev 13–20: "the 14:00 Lisbon second edition, designed,
costed and approved" — carrying FRED actuals, landing 30 minutes after the
08:30 ET prints.)* Kabil killed it: **he is at the desk when data prints, so a
brief reporting the number after it lands tells him what is already on his
screens.** It is replaced by a pre-NY-open delta at ~07:45–08:15 ET (D17, D18)
— deliberately *before* the print rather than after it.

**The honest cost:** three probe rounds (14, 15, 16) settled FRED's vintage
method for a claim the brief will now not make. §12.9 and §12.10 stand as
correct findings, and **most of that specific work is surplus to the design
that replaced it.** FRED itself survives, repurposed to BACKDROP —
unemployment trend, yield curve, CPI trend — which needs none of the
`output_type=4` vintage machinery. Recorded rather than quietly dropped,
because a planning chat that reverses four revisions of work should cost
something visible.

---

## §5 · OPEN QUESTIONS

### Blocking / high value
- ✅ **CLOSED 2026-09-08: install the Apps Script trigger.** Open since
  2026-09-05, the highest-value item for four days. Done, proven (§2.1b).
- ✅ **CLOSED 2026-09-13, same day it opened: the script is re-pasted and v7
  is live.** Apps Script logged `Brief dispatched 16:26 LIS (trigger v7)`,
  GitHub run #64 started `15:26:45Z`, the brief arrived `15:27:01Z` and
  carried **no** `TRIGGER OUT OF DATE` banner — so the version the script
  reports and the version this repo expects now agree, measured rather than
  assumed (§2.1f).
- ✅ **CLOSED 2026-09-13: the timer is intact** (was: ❓ not verified). The
  Triggers page shows exactly one trigger — owner *Moi*, time-based, function
  `sendBrief`, deployment **Head**, error rate **0%**, last run **13 Sep 2026
  09:20:11**. `Head` matters: the trigger runs the newest saved code rather
  than a pinned deployment, so the re-paste is live for tomorrow without any
  further step (§2.1g).
- ✅ **CLOSED 2026-09-18 — FIVE CLEAN MORNINGS. Delivery is solved.** Open in
  some form since rev 1; the headline item since rev 3. Five inbox timestamps,
  all 09:20 Lisbon, against a scheduler that was 13-for-13 late. §2.1h.
- ✅ **CLOSED 2026-09-18: the token-expiry blind spot (§3.26).** Found in the
  morning's plan, verified against the code, built, and fired in front of a
  reader the same day. §2.5 has the run. The fallback wording — the one
  7 November will actually produce — is offline-tested only, and §2.5 records
  that rather than counting it as proven.
- ✅ **CLOSED 2026-09-18: §3.24 is fixed.** Shipped with 17 tests. **Not yet
  seen firing live** — the NY Fed caught up before it shipped, so the first
  real proof is 28–29 October. Recorded as pending, not as proven.
- ✅ **CLOSED 2026-09-18: the offline suite really is offline now (§3.29).**
  It had been opening a live SMTP connection to Gmail on every run. 170s → 0.17s.
- ⏳ *(was: HIGHEST-VALUE ITEM: FED PATH's target range is stale for 1–2 days
  after every FOMC (§3.24).** Found the morning the measurement closed. It is
  in the shipping brief, it recurs eight times a year, and **the next FOMC is
  28 October**. Cheapest fix uses data already fetched: the watchlist knows the
  decision dates and POLICY DESK sees the statement land, so a range stamped on
  or before the last decision can be flagged as possibly superseded.
- ✅ **CLOSED 2026-09-18, seven hours after it opened: the outside task is
  deleted.** Kabil's call, taken the same day it surfaced — not rewritten as an
  alarm, removed. Its prompt is preserved verbatim in
  `docs/retired-cowork-relay.md`, with why it went and what to keep if a
  fallback is ever rebuilt, so deleting the job did not delete what it knew.
  The enabled-Routines list is now empty: **nothing outside GitHub Actions
  touches this project.**
- ⏳ *(was: NEW, and dated: a scheduled task outside this repository wakes up on
  26 October (§3.25).* It has self-exited every weekday since August on a
  seasonal guard. When Lisbon returns to winter time the guard stops firing and
  it runs for real at 09:45 LIS — with the ability to email a second, degraded
  brief to the same inbox. **Nothing needs doing today; everything needs
  deciding before the 25th.** Three options, in the order I would take them:
  **(a) rewrite it as an alarm** — keep the detection, drop the substitute
  brief, so a missing morning produces a one-line *"no cloud brief today"* mail
  instead of a search-sourced imitation of one; **(b) disable it** — the cloud
  path is 5-for-5 and the relay it was built to provide is now redundant;
  **(c) leave it** and accept a daily relay into a chat nobody reads.
  **Recommendation: (a), falling back to (b) if that is a week of work nobody
  wants.** It is his account and his inbox, so it is his call and not one to
  assume.
- ⏳ *(was: THE SINGLE HIGHEST-VALUE OPEN ITEM: five clean mornings.
  Running count: 4 of 5)* (was: 3 of 5 at rev 16; 2 of 5 at rev 12; 1 of 5 at rev 11; 0 of 5 at
  rev 9; 4 of 5, wrongly, at rev 6 — see §2.1d). Live table in §2.1h.
  Read the `built HH:MM LIS` line each day and compare against 09:25. Nothing
  else in this file matters until that number exists. The old schedule was ~40
  minutes late on its first two days before degrading to eleven hours, so one
  good morning is not evidence — and rev 6 proved that a *recorded* good
  morning is not even evidence that a brief was sent.
- ❓ **Does the gap detector actually fire in production?** It is tested
  offline and dry-run against live data, but it has never printed on a real
  morning. The next genuine miss is its first real test, and by construction
  nobody can schedule one.
- ⚠ **The gap detector inherits the state commit's reliability, and that is
  not measured.** `last_sent_date` only reaches the next run if the workflow's
  `Persist state` step pushes successfully. A push rejected as non-fast-forward
  — a commit landing on the branch between dispatch and push — would lose the
  marker and make the *following* brief report a gap that never happened. The
  step fails loudly if that happens, so it is detectable, and `concurrency:
  market-brief` serialises the runs themselves. **Deliberately not fixed in
  rev 7:** hardening the push is a change to the delivery path, and bundling it
  with the detector would mean shipping two untested things at once. A false
  alarm here would retire the detector within a week, so this is the first
  thing to watch.
- ⏳ **2026-11-07 — the trigger token expires.** The brief silently stops
  arriving on time when it does. Added to `data/watchlist.txt` so the brief
  counts down to it; Apps Script also emails Kabil when a trigger throws.

### Mechanics
- ⏳ FOMC dates in the watchlist (16 Sep, 28 Oct, 9 Dec) came from secondary
  sources. One click on the Fed calendar link confirms or kills them.
- ⏳ The 2026-11-04 quarterly refunding date is the conventional
  first-Wednesday slot, **not** a published announcement. Marked `CONFIRM` in
  the brief text itself.
- ❓ Does the policy radar surface anything on a quiet week? Two live runs both
  produced the same four entries. Needs a month of observation.

### Process
- ✅ **CLOSED 2026-09-17: the AHEAD horizon.** *(was: "Is the AHEAD horizon
  (130 days) right? Untested against Kabil's actual planning window."* Open
  since rev 1.) Answered: **365 days, five buckets** — NOW (7d) · THIS MONTH ·
  3 MONTHS · 6 MONTHS · 12 MONTHS — with a new per-entry `lead` field setting
  how many days ahead each one starts appearing, so a year-long horizon does
  not flood the section. `docs/BUILD_PLAN.md` §6.

### The build queue — gate cleared 2026-09-18, superseded by `docs/BUILD_PLAN.md`
*(was: "Queued behind the fifth clean morning", listing the 14:00 Lisbon "US
OPEN" edition, FRED and the news set as three independent items.)* The fifth
clean morning landed and **Gate 0 is cleared.** The three items survive but are
no longer a list — they are distributed across the five commits in
`docs/BUILD_PLAN.md` §9, and the 14:00 edition itself is reversed (§4.4).
Revised order in §13.

- ✅ **Commit 1 — DONE 2026-09-18.** Three tiers; CLOCKS; CYCLE with six
  expiry rules and a derived US holiday table; CALENDAR + RISK WINDOWS merged
  into TODAY; AHEAD to 365 days in five buckets; watchlist `class` and `lead`;
  FED PATH renamed EXPECTATIONS; the §3.24 fix folded in as planned. 381
  checks. **Deferred from it:** OVERNIGHT, whose own definition is *"what
  changed since yesterday's PM"* and which therefore cannot exist before the
  PM edition does.
- ✅ **The batched probe round — DONE 2026-09-18** (§12.11).
- ✅ **Commit 2 — DONE 2026-09-18.** Seven lines, every one out of a payload
  already fetched: annualised carry, perp basis, top-3 OI strikes a side,
  stablecoin supply and dominance, ETF streak, the cross-asset direction line.
  409 checks. **Deferred to Commit 4 with the state bundle**, because they
  need history the state file does not hold: range position 7d/30d,
  days-since counters, volume vs 30-day average, stablecoin 7-day change and
  BTC.D deltas.
- ✅ **Commit 3 — DONE 2026-09-18.** BACKDROP (FRED, round 16's explicit
  realtime window in code rather than only in this file) and NEWS (CNBC as the
  wire, ZeroHedge marked as commentary). 430 checks. Live on run #86.
- ✅ **Commit 4 — DONE 2026-09-18.** The state bundle (30-day history, `am`
  baseline, six new tracked figures) and the PM edition (spine + threshold
  body, NY-anchored, its own send marker, the shadow log). 475 checks. D21
  proven live on the first render (§2.6).
- 🟠 **Commit 5 — timing and health.** The Apps Script edit for the PM timers,
  then the five-dispatch observation. **The one remaining commit**, and the
  one that needs Kabil: a re-paste and a `SCRIPT_VERSION` bump.
- ⏳ **The deferred lines are unblocked but not built.** Range position
  7d/30d, days-since counters, volume against a 30-day average, stablecoin
  7-day change, BTC.D deltas. The bundle carries every field they need, and
  **none produces anything until the history has weeks in it** — which is the
  honest reason the schema shipped before the lines.

- ⏳ **Kalshi midterm contracts, deliberately not built.** The plan says Kalshi
  needs no probe because it is already LIVE and keyless. That is true of
  `KXFEDDECISION`; **the midterm control tickers are different contracts and
  nobody has looked at them.** §12.3 applies to them like anything else.
- 🟡 **`docs/BUILD_PLAN_ADDENDUM_1.md` — OPEN, and nothing in it is built.**
  Its own §1: *"a queue, not an instruction set."* Three additions (OI change
  against price, FRED liquidity plumbing, the CME weekend gap) plus three
  candidates recorded as proposed-and-not-taken. **The largest of those is
  liquidations** — see §12.2's `unconfirmed rather than settled` verdict and
  §12.4a.
- ✅ **CLOSED 2026-09-18: the nine probe targets are probed (§12.11).** Four
  pass, two fail, three inconclusive. Government hosts did **not** block the
  runner, which was the round's flagged risk. What remains open from it:
  - ⏳ **State Department, round 2.** Three guessed URLs, three dead ends —
    one of them a `200` serving a PNG. The `/rss-feeds/` index page answered,
    so the next round **parses it instead of guessing a fourth time**.
  - ⏳ **The Senate schema, and the House render.** `hearings.xml` answered
    200 and the probe's own parser could not read it. That is a probe bug, not
    a dead source.
  - ⏳ **Yahoo IBIT and Brent, re-probe.** Both drew `429`; the host never
    answered, so neither has been tested (§3.28).
  - ⏳ **The White House filter.** The feed is live and 2 of its top 3 items
    are irrelevant to markets. It wires behind §3.6's word list or not at all.
- ❓ **Five PM dispatch timestamps.** `nearMinute` behaviour is Google's
  scheduler, **not something a runner can probe** — the only test is to install
  it and watch. Recorded as an observation, explicitly not a probe. Cannot
  start until the Apps Script edit lands.
- ❓ **Threshold v2, range-scaled.** Blocked on probe target 3 (Kraken daily
  candles), then on ~2 weeks of shadow-log data.

### Data Kabil still owes
- ✅ **CLOSED 2026-09-15: the FRED API key.** Created and added as repository
  secret `FRED_API_KEY`.
- ✅ **CLOSED 2026-09-15: ZeroHedge in or out.** In, as visibly-marked
  commentary (D16).
- ⏳ **The events he already watches — moved for the first time since rev 1.**
  Four entries supplied in the 2026-09-17 chat: **Trump–Xi 24 Sep** (`policy`,
  lead 30, `CONFIRM`), **OpenAI court answer 1 Oct** (`policy`, lead 30,
  `CONFIRM`), **US midterms 3 Nov** (`statutory`, lead 60, derivable from
  federal law and therefore needing no confirmation route), **OPEC+
  ministerials** (~8/yr, `policy`, lead 14, hand-entered). Still the least
  complete item in the file, and no source can fill it.
- ⏳ **His manual morning checks** — what he looks at every day that the brief
  still does not carry. Raised in the 2026-09-17 chat and not answered.
  **This is where the remaining value is**; the cheap wins are close to
  exhausted.
- ⏳ Whether he wants any Fed speaker beyond Warsh tracked by name.

---

## §6 · FILE MAP

```
.github/workflows/
  market-brief.yml         two cron slots, secrets, guard wiring, state commit
  tests.yml                offline suite on every push (state/ ignored)
  probe.yml                manual source probe — the discipline in §12
  probe-permissions.yml    manual token-scope experiment (§2.2)
scripts/
  sources.py   (1265)      one adapter per source; each raises or returns real data
  render.py    (1030)      markdown + HTML; every unavailability handled explicitly
  main.py       (230)      run guard, orchestration, SMTP, recipient lock
  state.py      (102)      day-over-day memory + duplicate-send guard
  watchlist.py  (150)      the curated half of the policy radar; `class` and
                           `lead` per entry (was: 98 lines, five fields)
  cycles.py     (205)      recurring expiries and US market holidays, all by
                           rule. Nothing here makes a request, so it is right
                           a year out and never wrong because a feed was down
  health.py     (200)      does the brief itself still work — missed days,
                           stale trigger, and late arrival. The only module
                           that checks the system rather than the market
                           (was: 119 lines, two checks)
  probe.py      (167)      scratch prober, rewritten each round
tests/
  test_brief.py(1176)      offline, no network, gates every brief
data/watchlist.txt         dated events Kabil maintains by hand
state/latest.json          yesterday's figures, committed by the run itself
trigger/apps-script.gs     the on-time trigger — installed 2026-09-08; carries
                           SCRIPT_VERSION, which the brief checks (was: "NOT
                           YET INSTALLED", stale since 2026-09-08)
docs/trigger-setup.md      its walkthrough, checkpoint by checkpoint
docs/retired-cowork-relay.md  the scheduled task deleted 2026-09-18, its
                           prompt kept verbatim so deleting the job did not
                           delete what it knew
docs/BUILD_PLAN_ADDENDUM_1.md  the 2026-09-18 addendum. **OPEN** — a queue,
                           not a spec, and nothing in it is built
docs/BUILD_PLAN.md         the 2026-09-17 plan, verbatim, with a dated
                           reconciliation preamble. Nothing in it is built
docs/SYNOPSIS.md           the narrative account — the story, not the system
README.md                  setup, source table, design rationale
PROJECT_STATE.md           this file
```

---

## §7 · THE BRIEF IN BRIEF

**Three tiers** *(was, rev 1–23: a flat list of nine, then eleven,
sections)*, all Lisbon-time. The diagnosis behind the change: the brief did
not lack sections, it lacked hierarchy, and eleven sections typeset with equal
authority is the condition that let a $6bn buyback read as broken data (§3.9).
**If Tier 1 does not work as a standalone first screen, the redesign has
failed regardless of Tiers 2 and 3.**

Seven days a week since 2026-09-12 (D14). A weekend brief carries no
cash-session windows and states that, rather than printing an open and a close
that will not happen.

**TIER 1 — the first screen.** About fifteen lines, and most mornings it is
the whole brief.

| Section | Content | Source |
|---|---|---|
| **CLOCKS** | LIS · UTC · NY · TYO, plus the state of three sessions — *"New York opens in 5h10m"*. Every offset from the zone database, never assumed | derived, no fetch |
| THE SETUP | Three lines: BTC with day-over-day delta and range position, top USD risk today, latest ETF flow | derived |
| **TODAY** | **CALENDAR and RISK WINDOWS merged** — every event and window still ahead, in one chronological list, with forecast and previous riding the line. Weekends and **US market holidays** suppress the cash session | ForexFactory + derived |
| **CYCLE** | Six recurring expiries, each inside its own lead window; **silent most mornings by design**. Names the front-expiry roll on Deribit settlement days | derived, no fetch |

**TIER 2 — the standing picture.**

| Section | Content | Source |
|---|---|---|
| CRYPTO | BTC/ETH/SOL with deltas, ranges, VWAP; max pain and **the top three OI strikes a side, with contract counts** | Kraken + Deribit |
| FLOWS | BTC ETF net flow, per-fund, 6-day run with sign-flip flag **and the streak in days** | TFTC (CC BY 4.0) |
| DERIVATIVES | Perp funding, **the same rate as an annual carry**, **basis against the index**, and OI | Deribit, single venue, labelled |
| SENTIMENT | Fear & Greed with day and week deltas; total mcap and dominance; **stablecoin supply *and* dominance (D24)** | alternative.me + CoinGecko |
| MACRO & EQUITIES | **One line of directions**, then DXY, 10Y, gold, WTI, VIX, S&P and Nasdaq futures, each with an age stamp | Yahoo chart API ⚠ §3.28 |

**TIER 3 — the horizons.**

| Section | Content | Source |
|---|---|---|
| **AHEAD** | The forward calendar, then every dated policy event — **365 days in five buckets**, each entry appearing once inside its own `lead` | ForexFactory + Federal Register + watchlist |
| **EXPECTATIONS** *(was FED PATH)* | Target range **with a supersession flag (§3.24)**, EFFR, priced odds, CPI/core/PPI | NY Fed + Kalshi + BLS |
| **POLICY DESK** | Warsh remarks and FOMC releases; buyback sizes; coupon auction calendar | Fed RSS + Fiscal Data + TreasuryDirect |
| **BACKDROP** | Unemployment, the 10Y–2Y spread, CPI as y/y **and 3-month annualised** — each with the day it was observed | FRED, explicit realtime window (§12.10) |
| **NEWS** | Four headlines a source over an 18h window, newest first, each with its age. **A ZeroHedge item is marked commentary, not a wire (D16)** | CNBC + ZeroHedge |

**The calendar carries no `actual`.** `sources.py:143`: *"ForexFactory weekly
feeds. Schedule-only: there is no `actual` field."* So the brief can print what
a number is forecast to be and never what it came in at — which is the whole
reason a second daily edition needs a release source of its own before it is
worth sending *(was, rev 1–9: "with actual/forecast" — ❌ WRONG, the source has
no such field)*.

Subject line carries date, BTC, next USD event, and a policy date if it is
within 7 days. The `Market Brief - ` prefix is load-bearing for the chat-side
Mode Check and must not change.

---

## §8 · WORKING AGREEMENTS

**Verification discipline.** No source is described as working before it has
answered a probe from an Actions runner and its payload shape has been read.
No number reaches the brief that was not fetched in that run. When a claim
rests on documentation or community consensus rather than a measurement, say
so — and then go measure it (§2.2 is what that looks like).

**Walkthroughs.** Kabil is not a coder and has said so. Anything requiring his
action is numbered, with a checkpoint after each block stating what he should
be seeing. Screenshots are read carefully — three secret-configuration mistakes
were caught that way in session 3.

**Feedback style.** Brutal honesty. No filler encouragement. Praise must be
specific and evidence-backed or it reads as noise.

**Own errors loudly.** D8 is retracted in the decision table where the live
decisions are, not in a footnote, with the measurement that killed it. The
`ff_calendar_nextweek` misdiagnosis, the inverted flow-flip flag, the
`should_run` argument that was ignored, and the "Contents: write" claim are all
recorded rather than quietly corrected.

**⚠ CHECK THE INBOX, NOT THE INTENT.** A delivery exists in exactly one place:
`kabil.dh@gmail.com`. A run log says a job ran, a commit says code changed, and
neither says a brief arrived. Every row of §2.1d that turned out to be wrong
was written from a run log or from an intention. **Before writing ✅ against a
morning, search the mailbox for it.**

**⚠ THE COMFORTABLE-WORK TRAP IN THIS DOMAIN: adding another data source
instead of installing the trigger.** Probing a new API is engaging, produces
visible output, and carries no discomfort. Installing the trigger is fifteen
minutes of clicking through Google's consent screens and is the only work that
changes the outcome. Session 7 added two whole sections to a brief that has
never once arrived on time. **When this file is next read, check §5 before
§12: if the trigger is still uninstalled, that is the work.**

---

## §9 · THE LOOP FROM HERE

```
1. Trigger fires 09:25 LIS  ->  dispatch  ->  run starts in seconds
2. Self-test gates the build (offline suite must pass)
3. ~18 sources fetched, each wrapped so a failure degrades one line
4. health.py checks the SYSTEM: missed days, stale trigger  ->  banner if wrong
5. Brief rendered, emailed, state committed
6. Scheduled cron fires late  ->  sees last_sent_date  ->  exits silently
7. The inbox is read FIRST, the run log second  ->  §2.1h row
8. Weekly: confirm watchlist entries, add events he hears about
9. New source proposed  ->  PROBE FIRST  ->  §12.2 entry  ->  only then wire

   -- gate 0 cleared 2026-09-18; build order now docs/BUILD_PLAN.md §9 --
10. health.py latency banner: closes §3.26, the hole nothing detects
11. Probe round (9 targets, 1 dispatch) -- off the delivery path, runs parallel
12. Commit 1: three tiers, with the §3.24 fix folded in
13. Commits 2-5: data lines -> probed sources -> PM delta + state bundle -> health
```

**What success in this phase actually is.** Not a longer brief. A brief that
lands before the European open, five mornings out of five, with every number
carrying its source and its age. A brief with eleven sections that arrives at
13:00 is a failure. A brief with eight sections that arrives at 09:20 every day
is the goal. **The section count is not the metric; the arrival time is.**

---

## §10 · SESSION LOG

| # | Date | What happened |
|---|---|---|
| 1 | 2026-08-21 | v3 prompt run in chat. Discovered the repo was empty — the 09:30 cloud job did not exist. Sandbox egress blocked every primary source; brief built from search + Kabil's own ForexFactory alert emails |
| 2 | 2026-08-21 | Built the workflow, sources, renderer, tests. `GITHUB_EVENT_SCHEDULE` rejected — reserved prefix — renamed `BRIEF_SCHEDULE` |
| 3 | 2026-08-25 | Gmail App Password setup. Three configuration mistakes caught from screenshots. First successful email |
| 4 | 2026-09-01 | MCP/skill candidates evaluated and rejected: MCP is client-side, no host in CI; skills are prompts and need an LLM call. Zero-cost line held |
| 5 | 2026-09-05 | Gap analysis, then Phases 1, 3, 4: stale-quote stamps, risk-window filtering, day-over-day state, ETF flows via TFTC after Farside 403s, derivatives via Deribit after Binance 451s |
| 6 | 2026-09-05 | Token scope measured (§2.2), D8 retracted. Apps Script trigger + walkthrough written and committed. **Not installed** |
| 7 | 2026-09-05→06 | AHEAD section (probe rounds 4–6). Live run exposed three noise entries including `trade`⊂`Trademark`; two-tier filter shipped with regression tests. POLICY DESK for Warsh/Bessent/buybacks (rounds 7–9). This file created |
| 8 | 2026-09-07 | `testNow()` added so the trigger install can be proved at a weekend. Walkthrough delivered. **Kabil reported no brief at 11:22 Lisbon; investigated and confirmed the scheduler had not fired 1h57m past target (§2.1a). Sent manually.** The failure this project has been describing for three weeks, observed live |
| 28 | 2026-09-20 | **Commit 5 closes itself.** The morning brief dispatched from Google carrying `TRIGGER_VERSION: 8` and the PM edition fired at **12:00:09Z — 13:00 Lisbon to the second** — `sendPm` exists only in v8, so it is proof twice over of the thing rev 29 had to mark amber. Both sent; the PM wrote its marker and left the daily baseline alone. Saturday's PM had gone out 3h26m late via the **cron fallback**, which is the fallback doing its job and saying so. Then reading the delivered brief found two more defects the suite had never seen: `2th straight inflow`, and **bank reserves printed as three quadrillion dollars** because two layers each asserted a unit and neither checked it (§3.38). Probe round 20 asked FRED rather than guessing a second time |
| 27 | 2026-09-19 | **Commit 5 and the first PM editions — five bugs, none of which a test could have caught.** Probe round 19 sized the OKX page (100 rows / 28 minutes) and settled that `sz` is in contracts, so liquidations ship as counts and skew with **no dollar figure**. The addendum was closed by building all of it. Then Commit 5 installed the PM timers and bumped the trigger to v8 — Kabil re-pasted, three timers confirmed, banner cleared. **Then the running started, and it found what reading had not:** the PM cron fallback was inert and its test only checked that a string was present (§3.33); `BRIEF LATE` judged every PM edition against the morning's 09:25 target and would have fired on half of all briefs for ever (§3.34); and the PM edition announced Friday's session as today's, poisoning the first row of the D20 shadow log on the way (§3.35). Then Kabil's weekend call (D25) and two more found while verifying it: the PM edition waited on FRED, which it never prints — 100s inside FRED's maintenance window against 4s after the fix (§3.36) — and the shadow log had been recording `skip_email` test dispatches as if they were editions (§3.37). **All five were found by dispatching, not by reading** — the suite was green through every one of them |
| 26 | 2026-09-18 | **Probe round 18 and Commit 4.** The round overturned a verdict carried since rev 1: OKX returns liquidation orders keyless, with size, timestamp and side, so **the largest gap between Kabil's framework and this system is a wiring job rather than a subscription** (§3.31). Three other results corrected things this file asserted, two of them my own errors. Then Commit 4 — the state bundle and the PM edition, **the largest change on the delivery path** — with D21 proving itself on the first live render (§2.6). Two bugs of mine inside it: a per-cent change compared against a basis-point threshold, which would have fired the body on almost every afternoon, and a "still ahead today" line printing tomorrow's entry (§3.32) |
| 25 | 2026-09-18 | **Commit 3 — BACKDROP and NEWS.** The FRED work repurposed from release-minute actuals to the economic picture, with round 16's explicit realtime window written into the fetcher rather than only into this file. NEWS ships CNBC as the wire and ZeroHedge marked as commentary — and the first live run returned three ZeroHedge items of which one was a culture-war headline with no market content, which is D16's warning arriving as evidence (§3.30). Two of my own mistakes: the commit message claimed 443 checks when the suite reports **430**, and `FRED_API_KEY` had been wired into `probe.yml` and never into the job that builds the brief, so BACKDROP would have degraded to `unavailable` every morning — caught by dispatching rather than by reading |
| 24 | 2026-09-18 | **Commit 2 — seven lines, no new requests.** Funding restated as an annual carry (a rate per 8h is abstract; the same number annualised is money), perp basis pulled from a ticker field that was always in the payload and never returned, three OI strikes a side instead of one, stablecoin supply *and* dominance enforcing D24 in code, the ETF streak, and a cross-asset direction line. Three tests exist only to keep interpretation out: the options line may not say pin/target/support/resistance/expect, MACRO may not say risk-on or bearish, and dominance may not appear on a line without supply |
| 23 | 2026-09-18 | **Commit 1 — the brief gets a shape.** Three tiers, CLOCKS, CYCLE, TODAY (CALENDAR + RISK WINDOWS merged), AHEAD to a year in five buckets, watchlist `class` and `lead`, EXPECTATIONS. **§3.24 fixed** and folded in as the plan said it should be — though the NY Fed caught up before it shipped, so it has not been seen firing. Two defects found by building rather than reading: `date` was missing from `render.py`'s import, which would have raised `NameError` on the first FOMC morning; and the offline suite had been opening a **live SMTP connection to Gmail on every CI run** (§3.29), which is why it took 170 seconds and now takes 0.17 |
| 22 | 2026-09-18 | **Probe round 17 — nine targets, one dispatch, five seconds.** Four pass (White House feed 30/30 dated; Kraken 721 daily candles giving a **2.43% 14-day ADR**, which unblocks threshold v2; CoinGecko already carrying `usdt`/`usdc`; CourtListener keyless over 1,355 dockets). Two fail. Three inconclusive — including two Yahoo `429`s that tested nothing about IBIT or Brent but revealed **eleven shipping lines on one rate-limiting host** (§3.28). Polymarket returned a well-formed 200 answering a different question: `tag=fed` silently ignored, an Ethiopian election market returned under `closed=false` three months after it closed (§3.27). And the probe's own parser wrongly reported the Senate feed as unreadable — logged as a probe bug, not a dead source |
| 21 | 2026-09-18 | **First build since the gate cleared.** The `health.py` latency banner shipped and fired live on run #78 — `BRIEF LATE — built 12:56 Lisbon, 3h31m past the 09:25 target` — closing §3.26 the same day it was recorded. D25 locked: a detector may only claim what it can tell apart, which is why the dispatch branch says *"unless this brief was pulled by hand"* and the fallback branch does not. Kabil ordered §3.25's task deleted outright rather than rewritten; done, with its prompt preserved. Probe round 17 dispatched: nine targets, one run |
| 20 | 2026-09-18 | Kabil shared `docs/BUILD_PLAN.md` — a full redesign produced in a separate planning chat on 17 Sep against rev 17. It reverses the 14:00 data-actuals edition (§4.4), reorganises the AM brief into three tiers, extends AHEAD to 365 days with a `lead` field, and adds D17–D24 plus a D11 amendment. Two of its claims were checked against the code before being recorded: **the token-expiry blind spot is real (§3.26); the `muteHttpExceptions` hole it describes was closed in v5 and needed no work.** Gate 0, which the plan assumed stood at 3 of 5, had cleared the same morning |
| 19 | 2026-09-18 | **Day 5 of five — delivery declared SOLVED.** Five inbox timestamps, all 09:20 LIS; dispatch identical to the second on all five days. The same morning found §3.24 — FED PATH had printed a target range the Fed superseded two days earlier — so the build queue five clean mornings was meant to unlock stayed shut. Closing the session for a handoff then surfaced §3.25: an enabled scheduled task firing daily outside the repository since August, dormant only because of a seasonal guard that stops guarding on 26 October |
| 18 | 2026-09-17 | Day 4. The brief moved on from the FOMC correctly — the countdown re-pointed at 28 Oct, the radar dropped the spent entry, and the rebuilt ETF sign-flip flag fired live. The `Target X–Y% · EFFR` line was recorded **UNREAD** rather than inferred from the EFFR beneath it, which had plainly updated. That refusal to infer is what produced §3.24 the next morning — the inference would have been wrong |
| 17 | 2026-09-16 | Day 3 of five, and the FOMC. Both radar legs fired on the same event and agreed; FED PATH resolved its countdown to `TODAY` with Kalshi live at 86% against 80% on the 13th; RISK WINDOWS listed all four components separately. **The ETF sign-flip flag — the detector the synopsis records as inverted at birth — was observed firing correctly on a real reversal for the first time** |
| 16 | 2026-09-15 | Probe rounds 15 and 16. FRED can carry *"came in at X"*: `output_type=4` returns the first print with `realtime_start` = its publication date, proven end to end on Empire State, which had published 3 minutes before FRED carried it. Two traps caught — the default realtime window wanders and must never be used, and `releases/dates` lists **scheduled** dates (FOMC projected daily to year end). §3.22 and §3.23 |
| 15 | 2026-09-15 | Day 2. Kabil added `FRED_API_KEY`; ZeroHedge decided IN as marked commentary (D16). The 14:00 Lisbon second edition designed and approved — corrected from his proposed 13:00, which is 08:00 ET, not 09:00. FRED's own maintenance window (Sat 19 Sep) added to the watchlist so the brief counts down to it |
| 14 | 2026-09-14 | Day 1 of five clean mornings, and the first delivery row in this file read from the inbox before anything else. Probe round 14: X costs $0.005/read with no free tier and Nitter is under cease-and-desist, so the four accounts were probed at source instead — **CNBC, which Kabil never named, beat three of his four** (§12.8). §3.20 and §3.21 |
| 13 | 2026-09-13 | **The seven-day switch had never taken effect.** Checked the inbox rather than the run log and found no brief for Sat 12 or Sun 13 Sep — the Google copy of the Apps Script still carried the weekend guard rev 6 removed from the repo, and §2.1d had recorded the Saturday as delivered. Sunday's brief sent by hand. Built the two detectors that would have caught it (`health.py`: missed days, trigger version) and fixed a third defect the gap exposed — a two-day move labelled "vs yesterday" (§3.18). Delivery record rebuilt from Gmail. **Kabil re-pasted within the hour; v7 confirmed live end to end (§2.1f)** |
| 12 | 2026-09-12 | Brief switched to seven days a week (D14). Both crons drop the weekday filter and the Apps Script trigger loses its weekend guard; the cash-session suppression stays and gains tests on a real Sunday and a real Monday |
| 11 | 2026-09-12 | FED PATH added: target range and EFFR (NY Fed), priced odds for the next decision (Kalshi), CPI/core/PPI computed from the BLS index and held until superseded. **D13's Fed-path clause retracted** — the odds were never unavailable, only CME's rendering of them was (§12.4a). Expected-market-reaction deliberately not built, with a test asserting the section never forecasts |
| 10 | 2026-09-10 | Kabil: the $6bn buyback announcement was missing. It was not missing, it was unreadable (§3.9). Four defects behind one line: a wrong verdict in §12.2, a string `"null"`, an unrequested column, and a cross-population median. Announced operations now lead the section with cap, Lisbon window and a bucket-aware step-up flag, and appear in RISK WINDOWS. Two of the four were caught only by dry-running against live data |
| 9 | 2026-09-08 | **Trigger installed and proven (§2.1b).** Four failed token attempts first, from two silent GitHub UI traps (§3.9) — the second caught only because the token was dispatch-tested before the Google setup. Duplicate guard confirmed working in production against yesterday's 6h42m-late run (§2.1c). The project's blocking item since 2026-09-05 is closed |

---

## §11 · CHANGE LOG

**Rules.** Field-level, newest first. Every entry names its type and its
evidence. `Not changed, deliberately:` is a required line wherever restraint
was exercised, because restraint that is not recorded reads as an oversight
later.

```
## rev N · YYYY-MM-DD · <one-line title>
**Sections touched:** §x, §y
**Type:** DATA / DECISION / CORRECTION / STRUCTURE
**Evidence:** <run id, commit, log line, or "Kabil, this session">

| Field | Was | Now |
|---|---|---|

**Why:**
**Impact on prior conclusions:**
```

## rev 30 · 2026-09-20 · Commit 5 closes itself, and the brief turns out to have been printing quadrillions

**Sections touched:** header, §3.38 (new), §10, §12.2
**Type:** DELIVERY / DEFECT
**Evidence:** runs #101–#105, probe round 20. 640 offline checks, 0.22s.

**COMMIT 5 IS CLOSED. The whole chain ran unattended, twice, and proved
itself:**

| | |
|---|---|
| Morning, run #103 | dispatch 08:26:13Z · `TRIGGER_VERSION: 8` · no banner · **sent** |
| PM, run #104 | dispatch **12:00:09Z — 13:00 Lisbon to the second** · crypto only · **sent** |

**`TRIGGER_VERSION: 8` came out of Google's own dispatch**, which is what rev
29 marked amber and said only a real firing could settle. It is settled.
`sendPm` exists **only** in v8, so #104 firing at all is a second, independent
proof of the same thing.

`PM marker written; the daily baseline is untouched.` — D21 working in
production on a real send, not a fixture.

**Saturday, for the record: the fallback earned its place.** The Apps Script PM
timer never fired on the 19th — almost certainly because `install()` was run
after 13:00 that day. The cron fallback caught it at **16:26 Lisbon** and the
banner said exactly which path had built it and why:

> *No brief had gone out today, so the fallback schedule built this one — the
> on-time trigger did not deliver.*

A second scheduled run at 17:14 exited in **0 seconds** on the PM duplicate
guard. Both halves of §3.33's fix, working, on their first real outing.

**And then reading the delivered brief found two defects no test had.**

- **`2th straight inflow`** — the streak counter hardcoded `th`. Fixed, teens
  included.
- **§3.38 — bank reserves printed as three quadrillion dollars**, every
  morning, because two layers each asserted a unit and neither checked it.

**The pattern is now five days old and has not changed once:** every defect
this week was found by *running* the thing and *reading the output*, never by
the suite. Seven in a row. §8's rule earns its keep daily; the corollary is
the one worth carrying — **a green suite is evidence about the fixtures, not
about production.**

> Also worth naming: a `state file unreadable (JSONDecodeError)` warning shows
> on every run's annotations and is **the test suite's own** corrupt-file test
> proving honest degradation. It is not a production fault, and it was nearly
> reported as one.

---

## rev 29 · 2026-09-19 · Commit 5 ships, and then three PM bugs fall out of actually running it

**Sections touched:** header, §3.33–§3.37 (all new), D25 (new), §10, §13
**Type:** DEFECT / DELIVERY
**Evidence:** runs #92 (12:34:44Z), #95 (13:20:21Z), #96 (13:31:17Z). 555
offline checks, up from 527.

| Field | Was | Now |
|---|---|---|
| Trigger | v7 installed, v8 in repo, banner showing | 3 timers confirmed by screenshot; **v8 still unproven from Google's side** |
| PM cron fallback | registered and **inert** (§3.33) | resolved in Python, and tested on behaviour |
| `BRIEF LATE` on a PM edition | **fires every day, for ever** (§3.34) | judged against the PM target, anchored to New York |
| Cross-asset in the PM body | fires on any quote (§3.35) | **freshness is a gate** |
| `shadow.jsonl` | rows from test dispatches, two fields measuring Friday | **only real sends are logged**; stale logs as `null` |
| `gather()` | 21 fetches for both editions | **lazy — PM fetches 9, morning still 21** (§3.36) |
| Liquidations | probed (§3.31) | **wired** — counts and skew, no notional |
| `BUILD_PLAN_ADDENDUM_1` | open | **closed, and all of it built** |

**Why this revision is mostly defects.** Commit 5 was the last commit in the
plan and the only one that could not finish without Kabil — he pasted v8 and
ran `install()`, and the Triggers page showed three timers. Everything after
that point was **found by dispatching runs, not by reading code**, and the
suite was green through all three.

> ⚠ **What the cleared banner does and does not prove.** Runs #95 and #96 were
> `workflow_dispatch` calls where **I supplied `trigger_version: 8` as an
> input**. They prove the banner clears when a dispatch carries v8. They prove
> **nothing about the copy running inside Google** — that claim can only be
> settled by a dispatch Google itself sends, i.e. the next scheduled brief.
> §12.4a: a verdict is a claim, and the claim here is still open. The screenshot
> shows three timers *exist*; it does not show their version.

**The pattern, stated plainly, because it is now the third time:**

| Bug | The suite said | What was wrong |
|---|---|---|
| §3.33 | green | the test asserted a string was **present**, not that it **worked** |
| §3.34 | green | no test had ever run `latency_note` as the PM edition |
| §3.35 | green | every PM fixture was written **without a timestamp** |

In all three, the test and the code agreed with each other and both were wrong
about the world. §8's rule — *nothing is working until a runner says so* — has
now paid for itself three times in one day, and the corollary is sharper than
the rule: **a green suite is evidence about the fixtures, not about
production.**

**What §3.35 cost that the other two did not.** A wrong banner is visible and
gets fixed. A wrong *dataset* gets averaged. The shadow log is the only
evidence that will ever exist for setting v2's thresholds, and its first row
was measuring the wrong day. That row is deleted — it came from a `skip_email`
test dispatch, not a real edition — and the file is back to empty, which is the
honest state.

**Proven live on run #96, in order:** the fixed `edition()` path renders the PM
edition; `BRIEF LATE` names `the 13:00 target`; all
four cross-asset quotes print `(Fri 18 Sep)`; MATERIAL CHANGE reads *"No
material change since 09:20"* where it had printed a false DXY alert.

**§3.36 — the PM edition waited on sources it never prints. FIXED.** Three runs
inside and outside FRED's maintenance window, same code path, same edition:

| Run | Built | FRED window | Build step |
|---|---|---|---|
| #95 | 13:20Z | outside | **13s** |
| #96 | 13:30Z | opens 13:30Z | **43s** |
| #97 | 14:25Z | inside | **100s** |

A call-graph trace over `pm_build` settles what the PM edition actually reads:
**11 of the 21 sources `gather()` fetches.** `backdrop` and `plumbing` — the
**nine FRED calls** — are not among them. With `TIMEOUT=30` and `tries=3` a
dead host costs 90 seconds, and nine of them share one host.

So the PM edition currently blocks on a source it does not render, and the
evidence is a 7.7× build time inside a window that was on the watchlist. The
morning brief has the same exposure: 08:20 UTC is outside FRED's maintenance
window, but *outside this particular window* is not the same as safe.

**FIXED, and not the way it was first scoped.** The obvious fix — a per-edition
list of what to skip — was attempted and abandoned, because **two attempts to
derive that list were both wrong, in two different ways**:

- an **AST trace missed `perp_eth`**, which is reached through a loop variable
  rather than a literal key;
- a **runtime recorder missed `plumbing`**, because the read sits inside
  `if backdrop is not None` and the fixture had no backdrop. *A measurement
  only ever sees the branches its data reaches.*

And the set is **data-dependent, not merely edition-dependent**: `perp_eth` is
needed only when the crypto-only block renders, which needs `cross_asset` to
succeed *and* be stale. A static list either over-fetches it every day or
misses it on the day it matters.

So `gather()` now returns a **`LazyContext`** that fetches a source the first
time something reads it. No list exists to drift, and a line added tomorrow
fetches its own source without anyone remembering anything. Iteration forces
everything, because `build()` ends by listing which sources failed and a
half-resolved context would under-report that — a degraded run claiming to be
healthy is §3.16 again.

> `dict.get` is implemented in C and never calls `__getitem__`, so `get()` is
> overridden explicitly. Without that, **every `ctx.get()` in the renderer —
> which is most of them — would have silently missed its fetch and read
> `None`.** That is the whole brief going blank, quietly.

**Measured on the runner, both editions, inside the same FRED window:**

| | Before | After |
|---|---|---|
| PM edition | **100s** (run #97) | **4s** (run #98) |
| Morning edition | 21 sources | **21 sources, unchanged** (75s, run #99) |

The morning edition still pays for FRED because it still **prints** FRED. That
is the correct outcome, not a missed optimisation.

**Closed by D25:** whether the PM edition should run at weekends. Kabil's call
— **crypto only**, and proven live on run #97: no cross-asset line, funding and
both liquidation books in its place, `Cash and futures markets are shut — crypto
only` in the subtitle.

---

## rev 28 · 2026-09-18 · Commit 4 — and D21 proves itself by accident on the first render

**Sections touched:** header, §2.6 (new), §3.32 (new), §5, §10, §13
**Type:** DATA / STRUCTURE
**Evidence:** run #87 `workflow_dispatch` with `BRIEF_EDITION=pm`,
2026-09-18 22:40:32Z, success. 475 offline checks.

| Field | Was | Now |
|---|---|---|
| `state/latest.json` | one snapshot | **30-day history + `am` baseline + 6 new figures** |
| The PM edition | designed and approved, unbuilt since rev 13 | **built, and rendered live** |
| D21 | a decision | **proven in production (§2.6)** |
| PM send guard | — | **its own marker, separate from the morning's** |
| Shadow log | specified (D20) | **shipping from day one** |
| The five deferred lines | blocked on a schema | **unblocked, and still unbuilt** |

**Why:** The plan and the addendum both called this the largest change on the
delivery path and said it needed its own testing attention. It got 40 new
checks, and the most important asserts the PM changes **exactly one key** and
leaves the history and the morning snapshot byte-identical.

**Impact on prior conclusions:** none reversed. D21 moves from decided to
demonstrated, and by accident — the branch's state file predates the bundle,
so the very first PM render hit the exact condition D21 was written for.

**Two bugs of mine inside one commit**, both caught before a reader saw them.

**A per-cent change compared against a basis-point threshold.** The 10Y rule
is 5bp; a +0.30% session on a 4.70 yield is **1.4bp**, so comparing `0.30`
against `0.05` would have fired the material-change body on almost every
ordinary afternoon — destroying the point of a delta edition inside a week.
Caught because a test fixture happened to carry a realistic yield.

**§3.32, the "still ahead today" line printing tomorrow's entry** — the fourth
time this project has met *present, sourced, correctly stamped, materially
misleading*.

**Not changed, deliberately:** three things.

**The five deferred lines are still deferred.** The bundle carries every field
they need and none produces anything until the history fills. Shipping the
schema first is the point, not a shortfall.

**The addendum's OI-change line was not built.** It rides this bundle's
prior-run OI field, which now exists, and lands cleanly when that document
closes.

**Nothing dispatches the PM edition yet.** Commit 5 is the Apps Script work,
and it is the one piece Kabil has to do himself.

---

## rev 27 · 2026-09-18 · A verdict carried since rev 1 falls to one keyless call

**Sections touched:** header, §3.28 (corrected), §3.31 (new), §12.2, §12.12 (new)
**Type:** CORRECTION / DATA
**Evidence:** probe run #18, job 105783755564, 2026-09-18 22:32:54–57Z.

| Field | Was | Now |
|---|---|---|
| Liquidations | `S2` — no free source, $29/mo, since rev 1 | 🟢 **free, keyless, with size, timestamp and side (§3.31)** |
| Bybit | never tried | ⚫ `S1` — **fourth geo/datacenter block** |
| Bitget | never tried | 🟡 ticker carries funding **and** OI — a second venue |
| Kalshi midterms | *"needs no probe"* (the plan) | ⚫ `S8` — four guessed tickers, four empty 200s |
| State Department | ⚫ excluded on three guessed URLs | 🟡 **20 real feeds, off its own index** |
| Senate schema | *"no items parsed"* | 🟡 **known** — and round 17's verdict was my parser |
| §3.28 Yahoo | *"rate-limits an Actions runner"* | ⚠ **overstated — probably my headers** |

**Why:** §12.4a says a verdict is a claim and claims decay. Three of this
round's eight results overturn something this file previously asserted, and
**two of the three were my own mistakes rather than the world's.**

**Impact on prior conclusions:** one reversal, one correction, one assumption
disproven.

**The reversal is the big one.** `CoinGlass · S2 · no free tier` has sat in
§12.2 since rev 1 and the register itself flagged it *unconfirmed rather than
settled*. One keyless call to OKX returned liquidation rows with sizes,
timestamps and `posSide`. **The largest gap between Kabil's stated framework
and this system — his own first principle is "liquidation cascades, not
support/resistance magic" — is now a wiring job, not a subscription.**

**The correction is mine, and it cuts against a finding I wrote this
morning.** §3.28 claimed Yahoo rate-limits Actions runners, on two rounds of
`429`. Round 18 re-probed on a second host and drew `429` again, which looks
like confirmation — until you notice the brief's own Yahoo calls succeeded in
four runs minutes either side of both probes, seven symbols, no failures. The
probe sends a browser User-Agent with a JSON `Accept`; `sources.py` sends
`{"User-Agent": UA, "Accept": "*/*"}`. **A browser fingerprint on an API
endpoint is an ordinary thing to rate-limit.** §3.28 is marked overstated
rather than deleted, and round 19 settles it by repeating the call with the
brief's own headers.

**The disproven assumption is the plan's.** *"Kalshi needs no probe — already
LIVE and keyless"* is true of `KXFEDDECISION` and false of the midterm
contracts: four guessed series tickers, four `200 {"markets":[]}`. **An empty
list at 200 is the quietest failure available** — no error, no 404 — and a
fetcher written on that assumption would have printed an empty block every
morning with nothing to distinguish *no markets* from *wrong ticker*.

**Not changed, deliberately:** two things.

**Nothing was wired.** OKX passed a strict test on one call returning five
rows of one underlying. The window it reaches, whether a 24h aggregate is
derivable without paging, and how it reads on a quiet day are all unexamined.
§12.3 has not moved.

**§3.28 was corrected, not deleted.** The `429`s happened and are recorded.
What changed is the claim built on them.

---

## rev 26 · 2026-09-18 · Commit 3 — and a warning that arrived as evidence three headlines in

**Sections touched:** header, §3.30 (new), §5, §6, §7, §10, §13
**Type:** DATA / CORRECTION
**Evidence:** run #86 `workflow_dispatch` 2026-09-18 22:23:07Z, success, no
`Degraded this run:` line — so both new fetchers returned. 430 offline checks.

| Field | Was | Now |
|---|---|---|
| BACKDROP | designed, FRED probed three rounds, unwired | **live** — UNRATE, 10Y–2Y, CPI y/y and 3m annualised |
| NEWS | decided (D16, §12.8), unwired | **live in BOTH editions** — Reuters (scoped) + CNBC as wires, ForexLive/CoinDesk/Cointelegraph as press, ZeroHedge marked commentary. PM window = since the morning brief (§3.39) |
| §12.10's rule | written in this file | **written in the fetcher** |
| D16's marking | a decision | **proven necessary on its first run (§3.30)** |
| Sections | thirteen | **fifteen** |

**Why:** Commit 3 is where the probe rounds finally buy something. Rounds
14–16 cost four dispatches and settled a method for a question that was then
cancelled; BACKDROP is that work repurposed rather than discarded.

**Impact on prior conclusions:** None reversed. §12.8's caution about
ZeroHedge is upgraded from a caution to an observation (§3.30) — one of three
live items was a culture-war headline. The marking held; the noise is real;
the choice is Kabil's.

**Two of my own errors, logged per §8.**

**The commit message for Commit 3 claims 443 checks. The suite reports 430.**
I wrote the number before the last test run rather than after it. The code is
unaffected and the message is now wrong in the history; correcting it here
rather than rewriting a pushed commit.

**`FRED_API_KEY` was wired into `probe.yml` and never into `market-brief.yml`.**
BACKDROP would have printed `unavailable — FRED_API_KEY is not set` every
morning: honest, correct, and useless. Found by dispatching a run rather than
by reading the workflow, which is §8's dry-run rule earning itself again.

**Not changed, deliberately:** three things.

**Kalshi midterms were not built.** The plan calls Kalshi probe-free because
it is already LIVE — true of `KXFEDDECISION` and unexamined for the midterm
control tickers, which are different contracts. Wiring them on that assumption
is exactly the shape §12.4a warns about.

**Nothing from the addendum was built.** It is marked OPEN by its own author
and says *"a queue, not an instruction set."* Two of its three additions
target Commits 1 and 3, both of which shipped today without them; they are
additive and land cleanly later.

**The White House feed is still unwired.** Round 17 passed it on mechanics and
its three newest items were saltwater angling, hunting heritage and Senate
withdrawals. It wires behind §3.6's word list or not at all.

---

## rev 25 · 2026-09-18 · Commit 2 — seven lines, and three tests that exist to keep opinions out

**Sections touched:** header, §5, §7, §10, §13
**Type:** DATA
**Evidence:** `sources.py` `perp_stats`, `options.summarise`,
`coingecko_global`; `render.py` `_annualised`, `_basis`, `_strike_list`,
`_streak`, `_cross_asset_line`; 409 offline checks.

| Field | Was | Now |
|---|---|---|
| Perp funding | a rate per 8h | **plus the same rate as an annual carry** |
| Perp basis | in the payload, never returned | **printed, and labelled live against funding's lag** |
| Options OI | one strike a side | **three a side, with contract counts** |
| Stablecoins | absent | **supply and dominance together (D24)** |
| ETF flows | a 6-day run | **plus the streak in days** |
| Cross-asset | five rows | **one direction line above the five rows** |
| New requests | — | **none** |

**Why:** All seven were on the plan's zero-cost list, and probe round 17 moved
stablecoins onto it by finding `usdt` and `usdc` already inside the `/global`
call. Line count is the real cost, not code: **Kabil's worst bug was data that
was present, correct and unread**, so each line had to justify itself before
it was printed.

**Impact on prior conclusions:** None reversed. D24 moves from a written rule
to an asserted one — a test now fails if dominance is ever printed on a line
without supply beside it.

**And the 365-day horizon earned itself on its first live run.** Run #84's
AHEAD carried a **6 months** bucket containing *"T-144 · Tue 09 Feb —
Adjusting Imports of Unmanned Aircraft Systems … Into the United States"*. At
the old 130-day horizon that entry did not exist. A Section 232 action with a
dated effective day, 144 days out, was invisible to the brief yesterday and is
in it today — which is the whole argument for a year of range, made by the
data rather than by me.

The same run confirmed D11's per-class horizons working as designed: the two
hand-entered dates (Trump–Xi, OpenAI) render `⚠ never confirmed`, while the
midterms — `statutory`, verified the same day — render clean. *Evidence: run
#84, 2026-09-18 22:02:18Z, success.*

**Three of the new tests exist only to keep interpretation out**, which is the
part worth recording. The options line may not contain *pin*, *target*,
*support*, *resistance* or *expect*. MACRO may not contain *risk-on*,
*risk-off*, *bullish* or *bearish*. Annualised funding may not be described as
projected. **D3 and D9 were prose; they are now executable.** The temptation
they guard against is real and specific: the cross-asset line assembles five
moves into one glance, and naming that glance *"risk-on"* would have been the
brief's first opinion about the market.

**Not changed, deliberately:** two things.

**Five lines were deferred, not dropped** — range position 7d/30d, days-since
counters, volume against a 30-day average, stablecoin 7-day change, BTC.D
deltas. Every one needs history `state/latest.json` does not carry. The plan
puts that schema change in Commit 4 and bundles four features behind it, and
shipping a state change early for a feature that produces nothing for a month
is the wrong trade.

**Nothing from round 17 was wired here either.** Commit 2 is defined as
output-only; the probed sources are Commit 3.

---

## rev 24 · 2026-09-18 · Commit 1 — the brief gets a shape, and two defects fall out of building it

**Sections touched:** header, §3.24, §3.29 (new), §5, §6, §7 (rewritten), §10, §13
**Type:** STRUCTURE / CORRECTION
**Evidence:** commits on `claude/daily-market-brief-kvfi35`; run #82
`workflow_dispatch` 2026-09-18 18:46:57Z, success; 381 offline checks.

| Field | Was | Now |
|---|---|---|
| Brief structure | eleven flat sections | **three tiers, thirteen sections** |
| CALENDAR + RISK WINDOWS | two lists of the same day, in two places | **merged into TODAY**, one chronological list |
| AHEAD horizon | 130 days, three buckets | **365 days, five buckets, per-entry `lead`** |
| Watchlist fields | five | **seven** — `class` and `lead`, both optional |
| D11 confirmation horizon | 75 days for everything | **per class** (§4.2, now implemented) |
| US market holidays | not detected; a holiday printed an NYSE open and close | **derived by rule** in `cycles.py` |
| Deribit 08:00 UTC roll | invisible | **named on the morning it happens** |
| FED PATH | a stale range with no flag | **EXPECTATIONS, with a supersession flag** |
| The offline suite | opened a live SMTP connection to Gmail | **offline. 170s → 0.17s** |
| Curated events Kabil trades around | four, none in the file | **four, in the file** |

**Why:** The plan's diagnosis was right and worth implementing exactly as
written: the brief did not lack sections, it lacked hierarchy. Adding three
more to a flat list of eleven would have made the $6bn-buyback failure more
likely, not less.

**Impact on prior conclusions:** §7 is rewritten rather than amended — it
described a nine-section flat list that no longer exists. §5's oldest open
question, the AHEAD horizon, is closed in code as well as on paper.

**Two defects surfaced by building rather than by reading**, which is the
argument for §8's rule about dry-running against live data:

- `date` was absent from `render.py`'s `datetime` import. The new §3.24 check
  uses `isinstance(when, date)`, so **the first FOMC morning would have raised
  `NameError` inside the renderer.** The offline suite was green, because the
  branch is unreachable without an FOMC statement in the feed. Caught by
  exercising the path, not by reading it.
- §3.29, the live SMTP connection. Found by asking why the suite had got slow
  rather than raising the timeout, which is what the schedule wanted.

**Not changed, deliberately:** three things.

**OVERNIGHT was not built.** Its definition is *"what changed since
yesterday's PM"*, and there is no PM edition. Building it against yesterday's
morning instead would be a different section wearing the same name.

**Nothing from probe round 17 was wired.** Four targets passed. §12.3 puts
🟡 PROBED before 🟠 WIRED, and the White House feed is the argument for the
gap: it passes every mechanical test and its three newest items were about
saltwater angling, hunting and Senate withdrawals.

**The §3.24 fix is not recorded as proven.** It shipped, 17 tests cover it,
and it has never been seen firing in a delivered brief. 28–29 October.

---

## rev 23 · 2026-09-18 · Nine probes, and the two most useful answers were to questions nobody asked

**Sections touched:** header, §3.27 (new), §3.28 (new), §5, §10, §12.2, §12.11 (new)
**Type:** DATA / CORRECTION
**Evidence:** probe run #17, job 105590900580, 2026-09-18 11:59:41–11:59:46Z.
Every figure below is a line in that log.

| Field | Was | Now |
|---|---|---|
| Nine probe targets | 🔴 none probed, four sets of guessed URLs | **4 pass · 2 fail · 3 inconclusive (§12.11)** |
| Government hosts | flagged as a plausible `S1` | **whitehouse.gov answered a runner, 200, 30 dated items** |
| Threshold v2 (D19) | blocked on trailing candles | **unblocked — 721 candles, 14-day ADR 2.43%** |
| Stablecoin lines (D24) | 1 probe, cost unknown | **zero cost — already in the `/global` call** |
| The 1 Oct OpenAI date | no confirmation route | **CourtListener, keyless, 1,355 dockets** |
| Polymarket | `S7` 🟡 PROBED, "not wired: slugs are per-month" | `S8` ⚫ **EXCLUDED — filters accepted and ignored (§3.27)** |
| Yahoo | one source among eighteen | **a host carrying eleven lines that rate-limits runners (§3.28)** |
| Rubio | tracked by nothing | **still tracked by nothing** |

**Why:** The build order put the probe round second because it is the only work
that produces new facts rather than new plans. It did — and two of the three
most useful results were not on the target list.

**Impact on prior conclusions:** One register verdict reversed and one risk
promoted from theoretical to measured.

**Polymarket's row is downgraded**, `S7` 🟡 → `S8` ⚫. Rev 12 recorded it as
*"200, and far more liquid than Kalshi on the September meeting"*, unwired only
because its slugs carry a month. That was true and it was not the problem. The
problem is that its filters are **accepted and ignored**, so the failure is
invisible: a fetcher would have printed an Ethiopian election's odds under
*"Priced for the next decision"*. Liquidity was never the question.

**Yahoo's concentration stops being a note and becomes a finding.** The build
plan flagged it on 17 September as something to record; on the 18th a runner
drew a `429` from it. Eleven live lines, no fallback, one host, one rate limit.

**And I logged my own bug loudly**, per §8. The probe reported the Senate
hearings feed as unreadable. The feed answered `200` with 23KB of XML; the
parser looks for RSS `item`/Atom `entry` elements and the Senate uses its own
schema. **Recording that as a dead source would have been §12.4a's mistake for
a third time, caused by my code rather than by the host.** It is `S7`.

**Not changed, deliberately:** three things.

**Nothing was wired.** Four targets passed and not one line of fetcher was
written. §12.3's ladder puts 🟡 PROBED before 🟠 WIRED, and the White House
feed is the clearest case for why: it passes every mechanical test and two of
its three newest items are about hunting and fishing.

**The Yahoo concentration was not fixed.** A fallback for eleven lines is a
project, not a commit, and inventing one on the day the risk was measured would
be the comfortable-work trap (§8) wearing a safety vest.

**§3.24 is still not fixed** — third day, visible again in run #78. Commit 1.

---

## rev 22 · 2026-09-18 · The brief learns to say that it was late

**Sections touched:** header, §2.5 (new), §3.26, §4.5 (new), §5, §6, §10, §13
**Type:** DATA / DECISION
**Evidence:** run #78 `workflow_dispatch` 2026-09-18 11:56:07Z, conclusion
success; annotation and rendered banner at log lines 11:56:32.986–.987.
`scripts/health.py` `latency_note`; 26 new checks in `tests/test_brief.py`.

| Field | Was | Now |
|---|---|---|
| §3.26 | 🔴 open, no detector at any step | ✅ **closed and proven in front of a reader** |
| §3.25's scheduled task | 🟠 enabled, wakes 26 Oct | ✅ **deleted** — Kabil's call, same day |
| Things scheduled outside Actions | one, mail-capable | **none** |
| `health.py` | two checks, 119 lines | **three checks, 200 lines** |
| What a detector may claim | *(unwritten)* | **D25 — only what it can tell apart** |

**Why:** The plan found the hole, this file verified it against the code, and
the fix was the smallest change in the whole build order. Doing it first cost
one morning's work and removed the one failure mode that would have been
invisible while everything reported healthy.

**Impact on prior conclusions:** None reversed. §3.16's *"this project had no
way to detect its own absence"* now has its second half — it had no way to
detect its own **lateness** either, which is the harder case, because a late
brief still arrives and still looks like success.

**Not changed, deliberately:** three things.

**No Apps Script change, so no re-paste.** Adding a `manual` flag would let the
brief tell `testNow()` from a drifting timer, and would cost a
`SCRIPT_VERSION` bump to 8 — which makes every brief print `TRIGGER OUT OF
DATE` until Kabil re-pastes. That friction is not worth a distinction he can
make by remembering whether he pressed the button. D25 records the reasoning;
revisit when the PM timer forces a bump anyway.

**The 30-minute threshold was not tuned.** It is six times the largest spread
ever observed and no data yet says otherwise. Tightening it on five samples
would be exactly the over-fitting §12.4 warns about.

**§3.24 is still not fixed.** Run #78 shows it live for a third day:
`Target 3.50–3.75% · EFFR 3.63% · as of 16 Sep`, when the Fed moved to
3.75–4.00% on the 16th. It is next in the build order, inside Commit 1.

---

## rev 21 · 2026-09-18 · A redesign arrives from another chat, and two of its claims get checked

**Sections touched:** header, §3.26 (new), §4.1–§4.4 (new), §5, §6, §9, §10,
§13 (rewritten), `docs/BUILD_PLAN.md` (new)
**Type:** DECISION / CORRECTION / STRUCTURE
**Evidence:** `docs/BUILD_PLAN.md`, supplied by Kabil 2026-09-18 and committed
verbatim. Code checks run here: `scripts/health.py` `notes()`;
`.github/workflows/market-brief.yml:17-19`; `trigger/apps-script.gs:104-113`.

| Field | Was | Now |
|---|---|---|
| The second edition | 14:00 LIS, FRED actuals, *"came in at X"* — designed, costed, approved | **reversed (§4.4)**: a pre-NY-open delta at ~07:45–08:15 ET, before the print |
| AM brief structure | eleven flat sections | **three tiers, 14 sections** (D17–D24, `BUILD_PLAN` §3) |
| AHEAD horizon | 130 days, open since rev 1 | **365 days, five buckets, per-entry `lead` field** — question CLOSED |
| D11 confirmation horizon | 75 days for everything | **per-class: `policy` 75, `statutory` 365, `holiday` 365, `unlock` 30** (§4.2) |
| Token expiry 2026-11-07 | a dated watchlist entry | **§3.26 — a failure chain with no detector at any step** |
| `muteHttpExceptions` | *(plan: a silent-failure hole needing a fix)* | **already closed in v5 — verified, no work needed** |
| Events Kabil trades around | empty, unmoved since rev 1 | **four entries** — Trump–Xi, OpenAI, midterms, OPEC+ |
| Gate 0 | 3 of 5 (the plan's assumption) | **cleared 2026-09-18** |
| Fragile fortnight | 4 dated events, 25 Oct – 7 Nov | **6, three of them new since the plan** (§13) |

**Why:** The plan was written on 17 September against rev 17 and arrived on the
18th against rev 20. Left side by side and unreconciled, the two documents
disagree about the gate, about whether the PM edition carries actuals, and
about whether an Apps Script fix is needed. A handoff of two documents that
contradict each other is not a handoff.

**Impact on prior conclusions:** One reversal and one correction.

**The reversal** is §4.4 — the data-actuals PM edition is dead, and with it
most of the specific value of probe rounds 14–16. §12.9 and §12.10 remain
correct findings about FRED; they are simply no longer load-bearing, because
BACKDROP needs none of the `output_type=4` vintage machinery. Recorded openly:
a planning chat that reverses four revisions of work should cost something
visible.

**The correction runs the other way** — toward the plan. Its
`muteHttpExceptions` item describes a hole that `trigger/apps-script.gs` closed
in v5. Recorded in §3.26 so nobody spends a commit rebuilding a working guard.
**This is why a plan gets checked against the code before it gets built, not
after.**

**Not changed, deliberately:** four things.

**Nothing was built.** The plan is committed verbatim, with a preamble marking
what has moved. Gate 0 clearing removes the excuse for not building, not the
discipline governing how — nine unprobed targets are still nine unprobed
targets, and every URL in four of them is pattern-matched rather than verified.

**D17–D24 are recorded as design decisions, not measurements.** Their evidence
line is a document, which under §12.3 proves what was decided and nothing about
what works.

**§3.24 was still not fixed, and §3.25's task was still not disabled.**
Unchanged from rev 20, for the reasons given there.

**The plan's own §9 order was kept.** Two items moved — the §3.24 fix folded
into Commit 1, and the token renewal pulled out of the commit list because it
is an action only Kabil can take. The rest stands as written, because it was
right.

---

## rev 20 · 2026-09-18 · A scheduled task nobody in this file knew about, and the handoff

**Sections touched:** header, §1, §3.25 (new), §5, §9, §10, §13 (new)
**Type:** DATA / STRUCTURE
**Evidence:** Routines listing 2026-09-18 with `include_completed: true` — one
enabled entry, `trig_01T37HzNWDCP9qTWkrEgANre`, cron `45 9 * * 1-5`, last run
2026-09-17 09:45:54Z finishing 09:46:08Z; tz database Europe/Lisbon WEST→WET
2026-10-25.

| Field | Was | Now |
|---|---|---|
| Scheduled things outside Actions | none recorded | **one enabled weekday task, able to send mail (§3.25)** |
| That task's safety | (not known to exist) | **dormant by accident; active from 2026-10-26** |
| Its stated premise | *"two tasks are registered"* | **one exists; the summer slot is gone** |
| §10 session log | ends at #17 (2026-09-16) | **#18 and #19 written** |
| §1 "where it stands" | 2026-09-16, "three of five … two mornings remain" | **2026-09-18, measurement closed** |
| Handoff | — | **§13, naming what a new chat reads first** |

**Why:** The session is being handed to a new chat, and a handoff that lists
only the repository would hand over an incomplete system. The task in §3.25
sends mail to the same inbox as the brief, has been running since before this
file existed, and has a dated wake-up 38 days out. Recording it late is worse
than recording it now; not recording it at all is how the 12–13 September gap
happened.

**Impact on prior conclusions:** None reversed — every measurement in this file
still stands. But §3.16's scope is now visibly too narrow. *"This project had
no way to detect its own absence"* was fixed for the repository and is still
true of everything beside it: `health.py` catches a brief that did not arrive
and would not notice a second one that did.

**Not changed, deliberately:** three things.

**The task in §3.25 was not disabled.** It is Kabil's account, his inbox and
his fallback. It can send mail, which makes switching it off an outward-facing
change, and it cannot fire for another 38 days. Documenting it and recommending
an option is the correct action today; taking the action is not.

**§3.24 was not fixed.** The recommendation stands and the ordering decision is
still his. Fixing it unasked would be the same assumption in the opposite
direction.

**The build queue was not opened.** Unchanged from rev 19, and the reason is
unchanged with it.

---

## rev 19 · 2026-09-18 · Delivery is solved — and the same morning found a stale policy rate
**Sections touched:** header, §2.1, §2.1h, §3.24 (new), §5, §12.2
**Type:** DATA + CORRECTION

**Evidence:** five Gmail timestamps — `08:20:37Z`, `08:20:38Z`, `08:20:29Z`,
`08:20:36Z`, `08:20:33Z`, Mon 14 – Fri 18 Sep, every one 09:20 Lisbon. Five
`workflow_dispatch` runs (#65, #68, #71, #74, #77) all at `08:20:13Z`. Against:
FOMC statement 2026-09-16 raising the target range to 3.75–4.00%, and brief
runs #74 and #77 printing `Target 3.50–3.75% · as of 16 Sep`.

| Field | Was | Now |
|---|---|---|
| **Delivered-vs-target** | ❓ UNKNOWN since rev 1 | ✅ **SOLVED — 5 of 5 at 09:20 LIS** |
| Five clean mornings | 4 of 5 | **5 of 5, closed** |
| Dispatch precision | unclaimed at 4 samples | 5 of 5 at `08:20:13Z` — **recorded, and the doc's ±15min promise deliberately NOT narrowed** |
| NY Fed rates | 🟢 LIVE | 🟡 **DEMOTED** — EFFR fine, target range inherits its publication lag |
| FED PATH target range | assumed current | **stale for 1–2 days after every FOMC** (§3.24) |
| Highest-value open item | five clean mornings | **§3.24, before anything in the build queue** |

**Why:** The measurement that has headed this file since rev 3 is closed, and
the morning that closed it also produced the most consequential content bug
found since the $6bn buyback. Both belong in the same revision because the
second is the reason the first does not open the build queue as planned.

**Impact on prior conclusions:** §12.2's New York Fed row is corrected — its
verdict was true of EFFR and false of the target range's timeliness, which is
§12.4a's shape a third time: a property of one field recorded as a property of
the row. Nothing about the delivery result is affected; timing and content are
separate measurements and only one of them was being run this week.

**Not changed, deliberately:** three things.

The `docs/trigger-setup.md` promise of "roughly 09:10 to 09:40" stays wide
despite five identical dispatch seconds. Five observations describe behaviour;
±15 minutes is Google's stated contract. Narrowing it would train Kabil to read
an in-spec 09:35 arrival as a fault.

**The build queue is not opened.** The approved plan put FRED, the news set and
the PM edition behind the fifth clean morning, and the fifth arrived — but a
policy-critical bug in the *shipping* brief outranks three additions to it, and
the next FOMC is 28 October. Re-ordering the queue is Kabil's call, not an
assumption to act on.

And §3.24 is recorded without a fix attached. It was found by reading a line
this file had explicitly marked UNREAD the day before rather than inferring it
(rev 18) — the discipline worked, and shipping a same-morning fix on a Friday
to the path that just completed a five-day measurement is exactly the trade
that measurement exists to discourage.

## rev 18 · 2026-09-17 · Day 4 — the brief moves on, and a rebuilt feature fires live
**Sections touched:** header, §2.1h, §5
**Type:** DATA

**Evidence:** Gmail `2026-09-17T08:20:36Z`. Actions run #74,
`workflow_dispatch`, `2026-09-17T08:20:13Z`, head `7ea885c`. FED PATH:
`Priced for the next decision (T-41, settles Wed 28 Oct)`. POLICY DESK:
`⚠ ANNOUNCED — buyback TODAY · 18:40–19:00 LIS · up to $4.0bn · 7Y to 10Y`.

| Field | Was | Now |
|---|---|---|
| Five clean mornings | 3 of 5 | **4 of 5** |
| Dispatch second | 08:20:13Z three times | **four times** — claimed at five, not before |
| FED PATH after a decision | untested | ✅ re-pointed to 28 Oct, T-41; Kalshi rolled contracts unaided |
| Yesterday's FOMC | — | captured by the RSS leg as POLICY DESK history, not left as a stale forecast |
| Announced-buyback rebuild (§3.9) | fixed and dry-run only | ✅ **fired on a live $4.0bn operation** — led the section, cap and window carried, and in RISK WINDOWS |
| Target range after the decision | — | ⚠ **not read.** Above the log window inspected. Unchecked, not confirmed |

**Why:** Day 3 left one open question — whether a brief that renders a decision
correctly also stops counting down to it once it has happened. It does.

**Impact on prior conclusions:** None. Four of five is not five.

**Not changed, deliberately:** the target-range line is recorded as **unread**
rather than inferred from the Kalshi line beneath it, which plainly had rolled.
The inference is probably right and it is still an inference — and §3.17 exists
because this file once wrote down a plausible expectation as an observation.
The dispatch-second observation also stays unclaimed at four samples for the
same reason it stayed unclaimed at two and three.

## rev 17 · 2026-09-16 · Housekeeping pass — the narrative sections had drifted
**Sections touched:** header, §1, §5, §6, §9, §10
**Type:** STRUCTURE + CORRECTION
**Evidence:** Kabil, this session, asking for a full update. Line counts from
`wc -l`; section list from `render.py`'s own `md.append("## …")` calls.

| Field | Was | Now |
|---|---|---|
| §1 cadence | "every weekday" | **seven days a week** — D14 landed on 2026-09-12 and §1 was never updated |
| §1 section count | "nine sections", "nine live sources" | **eleven sections, ~18 sources** — FED PATH shipped rev 5 and §1 never caught up |
| §1 blocking item | "a two-minute re-paste by Kabil" | closed the same day it was written (§2.1f); §1 still carried it three revisions later |
| §1 diagnosis | "a measurement problem" | **"a sequencing problem, not a capability problem"** |
| §5 running count | 2 of 5 | 3 of 5 |
| §5 "Data Kabil owes" | 4 items | 2 closed, and the one that has not moved since rev 1 is now named as such |
| §6 `probe.py` | 95 lines | 167 |
| §9 loop | 8 steps, no health check, one edition | 10 steps, health.py named, inbox-first stated, PM edition placed **after** the fifth morning |
| §10 | ended at session 13 | sessions 14–17 added |

**Why:** Four days of daily revisions kept §2.1h, §3, §4 and §12 current while
the narrative sections silently aged. §1 was describing a nine-section weekday
brief blocked on a task finished three revisions earlier. **A state file whose
summary is stale is worse than one with no summary, because the summary is what
a new session reads first** — which is exactly how rev 6 put a false ✅ in
§2.1d.

**Impact on prior conclusions:** None. Nothing measured changes; this corrects
descriptions that had fallen behind the measurements.

**Not changed, deliberately:** §5's Mechanics and Process questions stand
unaltered — the FOMC dates still came from secondary sources, the refunding
date is still conventional rather than announced, and the radar has still not
been watched for a month. Three of those could have been quietly closed on the
strength of this week going well. None of them was actually checked, and
"nothing went wrong" is not the same as "it was verified" (§3.19).

## rev 16 · 2026-09-16 · Day 3, the FOMC, and a detector caught doing its job
**Sections touched:** header, §2.1h
**Type:** DATA

**Evidence:** Gmail `2026-09-16T08:20:29Z`. Actions run #71,
`workflow_dispatch`, `2026-09-16T08:20:13Z`, head `ed91482`. Subject:
`Market Brief - 16 Sep · BTC 75.4k -0.2% · Federal Funds Rate 19:00 · TODAY
FOMC decision + SEP / dot plo…`.

| Field | Was | Now |
|---|---|---|
| Five clean mornings | 2 of 5 | **3 of 5** |
| Dispatch second | 08:20:13Z twice | **08:20:13Z three times** — still not claimed; five samples first |
| FOMC rendering | untested on a live decision day | ✅ both radar legs agreed, all four windows listed separately, countdown resolved to `TODAY` |
| Kalshi odds | 80% on 13 Sep | 86% — the figure is live, not carried |
| ETF sign-flip flag | rewritten after being inverted; never seen firing on a real reversal | ✅ **fired correctly** after four outflow sessions |

**Why:** Day 3 of the measurement, and the one day this week where a
section-quality failure would have been expensive.

**Impact on prior conclusions:** None. Three of five is not five.

**Not changed, deliberately:** no trading content of any kind. Kabil scoped
this chat to the brief on 13 Sep and the FOMC does not reopen it — the decision
is a thing the brief must *render correctly*, which is what was checked, and
nothing more. The dispatch-precision observation also stays unclaimed at three
matching samples for the same reason it stayed unclaimed at two.

## rev 15 · 2026-09-15 · Round 16 — proven on a release that landed this morning
**Sections touched:** header, §3.23 (new), §12.2, §12.10 (new)
**Type:** DATA

**Evidence:** probe run 35030196370, job 104586657834. Empire State series
`AWCDINA066MNFRBNY`, initial releases newest-first: `realtime_start` =
`2026-09-15`, `2026-08-17`, `2026-07-15` against observation dates `2026-09-01`,
`2026-08-01`, `2026-07-01`. FOMC release dates: `2026-12-31 … 2026-12-26`.

| Field | Was | Now |
|---|---|---|
| Default realtime window | ⚠ suspected cache wobble | **confirmed unreliable** — `2026-09-04` twice today, `09-11`/`09-15` yesterday. Never use it |
| Explicit realtime window | untested | ✅ **honoured exactly** |
| `releases/dates` semantics | ⚠ unresolved | ⛔ **lists scheduled dates** — 2,965 in the forward window; FOMC projected daily to year end |
| "did this publish today?" | no reliable method | ✅ **the observation's own `realtime_start`** |
| FRED latency after a release | unknown | **~3 minutes** (`last_updated 07:33:29-05` for an 08:30 ET release) |

**Why:** Both of rev 14's cautions would have put a wrong date in front of a
reader. Round 16 was designed so each had a single decisive test rather than an
accumulation of hints — asking for *future* dates settles "scheduled or
published" in one call, and naming the window settles the cache question by
making it irrelevant.

**Impact on prior conclusions:** None reversed. §3.23 generalises the result
and links it to §3.17 — both are a plan being mistaken for an outcome.

**Not changed, deliberately:** still no FRED code, and the PM edition is still
unbuilt. Today is day 2 of five clean mornings; the plan's own §6 puts the
build after the fifth, and three decisive probe rounds in one evening are not a
reason to move a date set to protect the thing that already works.

## rev 14 · 2026-09-15 · FRED can say "came in", and a test that nearly proved nothing
**Sections touched:** header, §3.22 (new), §12.2, §12.9 (new)
**Type:** DATA

**Evidence:** probe run 35007629742, job 104511294765. Initial-release payload
verbatim: `{"realtime_start": "2026-09-04", "realtime_end": "9999-12-31",
"date": "2026-08-01", "value": "159075"}`.

| Field | Was | Now |
|---|---|---|
| FRED verdict | 🟡 PROBED — reachable, shape unknown | 🟠 **WIRED-READY** — carries the initial release *and* its publication date |
| "came in at X" | unsupportable by any wired source | **supportable** — `realtime_start` is the release date |
| Key handling in probes | round 14 used a hard-coded fake | real key from env, redacted from every printed URL; verified in the log |
| Release-date semantics | assumed usable | ⚠ **unresolved** — see §12.9 |

**Why:** This was the question the whole 14:00 edition rested on. It passed.

**Impact on prior conclusions:** None reversed. §3.22 is new and general: the
decisive test came within one field of proving nothing at all, because its
pass and fail produced the same two numbers.

**Not changed, deliberately:** **FRED is not wired.** Two things are unresolved
and both would put a wrong date in front of a reader: `realtime_start` came
back as `2026-09-11` on one call and `2026-09-15` on another seconds later
with no realtime parameter set on either, which suggests a cached response can
carry a stale "today"; and `releases/dates` listed an FOMC press release dated
today when the decision is tomorrow, so a listed date may mean *scheduled*
rather than *published*. §12.4 is explicit that a verdict from a single
observation gets re-tested before anything is built on it, and these are two
single observations pointing at the same risk. Round 16 settles them.

## rev 13 · 2026-09-15 · ZeroHedge in, and FRED wants an account
**Sections touched:** header, §4 D16 (new), §12.2, `data/watchlist.txt`
**Type:** DECISION + CORRECTION

**Evidence:** Kabil, this session. FRED's own API-key page: *"you cannot
request or view your API keys without first logging into your
fredaccount.stlouisfed.org user account."* Its maintenance banner: 19 Sep 2026,
08:30–10:00 Central = **13:30–15:00 UTC = 14:30–16:00 Lisbon**.

| Field | Was | Now |
|---|---|---|
| ZeroHedge | ❓ open since the probe | **IN** (D16), as visibly-marked commentary |
| FRED signup | "a free key" | **a full account login**. The walkthrough given to Kabil was wrong and was corrected to his face |
| FRED availability | assumed continuous | outage Sat 19 Sep, now counted down in the watchlist |

**Why:** Both were open questions blocking the PM edition's design. Neither
needed code.

**Impact on prior conclusions:** None. D16 does not weaken D4 — it is the
mechanism that lets non-fetched content exist without pretending to be fetched.

**Not changed, deliberately:** **no PM-edition code was written.** The approved
plan's §6 puts the build after the fifth clean morning and today is day 2. A
green approval is not a reason to start touching `main.py` mid-measurement —
that is exactly the trade §12.7's ladder exists to refuse. The watchlist entry
is the one exception, and only because `data/watchlist.txt` is plain text by
D10, is hand-edited by Kabil as a matter of course, and its parser skips and
reports a bad line rather than failing (verified: `problems: []`).

**Requires Kabil:** a `fredaccount.stlouisfed.org` account before the key can
be issued. Nothing is blocked until Friday.

## rev 12 · 2026-09-15 · Day 2, and a timer more precise than its own documentation
**Sections touched:** header, §2.1h, §5
**Type:** DATA

**Evidence:** Gmail `2026-09-15T08:20:38Z` — *"Cloud run — built 09:20 LIS.
The Setup BTC $76797, -1.2% vs yesterday"*, running straight into `## THE
SETUP`. Actions run #68, `workflow_dispatch`, `2026-09-15T08:20:13Z`, head
`316da27`. Prior day's dispatch: `2026-09-14T08:20:13Z`.

| Field | Was | Now |
|---|---|---|
| Five clean mornings | 1 of 5 | **2 of 5** |
| Day 2 arrival | — | 09:20 LIS, 5 min ahead of target |
| Dispatch precision | assumed ±15 min per Google's docs | **08:20:13Z on both days — the same second** |
| AHEAD radar | never observed reaching T-0 | the Canada tariff landed as `TODAY …` in the subject line |
| Duplicate guard | confirmed 13 Sep | confirmed again 14 Sep (run #67) |

**Why:** Day 2 of the measurement that §5 has headed since rev 3, and the
second row written inbox-first under §2.1h's rule.

**Impact on prior conclusions:** None. Two clean mornings is still short of
what §2.1 requires, and the old schedule managed two before degrading.

**Not changed, deliberately:** the `docs/trigger-setup.md` line promising
delivery "between roughly 09:10 and 09:40" stays as written. It is a safe
over-estimate and two samples do not justify narrowing a user-facing promise —
**if the timer misses once, the wide range is the honest one and the narrow one
would read as a broken guarantee.** Revisit at day 5. The PM edition and FRED
also stay untouched behind the remaining three mornings, per rev 10.

## rev 11 · 2026-09-14 · Day 1 of five, and it is the first row read from the inbox
**Sections touched:** header, §2.1h (new), §5
**Type:** DATA
**Evidence:** Gmail `2026-09-14T08:20:37Z` — *"Cloud run — built 09:20 LIS.
The Setup BTC $77724, +0.8% vs yesterday"*, running straight into `## THE
SETUP` with nothing between. Actions run #65, `workflow_dispatch`,
`2026-09-14T08:20:13Z`, head `616aaaf`.

| Field | Was | Now |
|---|---|---|
| Five clean mornings | 0 of 5, restarted rev 9 | **1 of 5** |
| Day 1 arrival | — | 09:20 LIS, 5 min ahead of target |
| Day 1 dispatch path | — | the Google timer, not a late cron |
| Both detectors on a healthy morning | untested in production | **silent, correctly** — no gap banner, no drift banner |
| `_vs_label` in production | tested offline and on a same-day rerun | `vs yesterday`, on a day when yesterday is genuinely the baseline |

**Why:** This is the first row in this file's delivery record that was read
from the inbox before anything else was consulted. Rev 7 had to correct a row
written the other way round, and §2.1h now says in its own header which
direction the evidence flows.

**Impact on prior conclusions:** None. It is one clean morning, which §2.1
has said since rev 3 proves nothing on its own — the old schedule was
near-punctual for two days before degrading to eleven hours.

**Not changed, deliberately:** the PM edition stays unbuilt and FRED stays
unwired. Both are queued behind the fifth clean morning precisely because they
touch the path that produced this row, and rev 10 already set that order. A
clean day 1 is not a reason to spend the remaining four.

## rev 10 · 2026-09-13 · Probe round 14 — the accounts were the route, not the fact
**Sections touched:** header, §3.20–§3.21 (new), §7, §12.2, §12.8 (new)
**Type:** DATA + CORRECTION
**Evidence:** probe run 34782212483, job 103791166562, ten candidates from an
Actions runner. FRED: `400 · "The value for variable api_key is not
registered"`. watcher.guru: `200`, 10 items, newest **41.9h old**. CNBC: `200`,
30 items, **54.8h window**, newest 3.1h. Yahoo news: `429`.

| Field | Was | Now |
|---|---|---|
| §7 CALENDAR description | "with actual/forecast" | **forecast and previous.** `sources.py:143` says the source is schedule-only and has no `actual` field — the claim was wrong in this file and in the synopsis |
| Release actuals | no source | **FRED reachable**, auth the only barrier. Needs Kabil to get a free key |
| The four X accounts | assumed relayable | one survives (@zerohedge), one is 42h stale (@WatcherGuru), one has no feed (@financialjuice), one has no free primary by design (@DeItaone) |
| Best news source found | — | **CNBC, which Kabil did not name**, beat three of his four |
| Freshness checking | quote age only | §3.20: nothing measured the *feed's* age. A 200 with well-formed timestamped items can still be two days behind |
| Host-collision risk | unconsidered | §3.21: Yahoo news `429`d, and Yahoo's chart API is the entire MACRO section |

**Why:** Kabil wants breaking news in the brief and named four X accounts. X
itself fails D2 outright — free tier killed 2026-02-06, pay-per-use at
$0.005/read, Nitter under cease-and-desist — so the question became which of
those accounts merely *relay* something reachable. Probing answered it, and
answered it differently than expected.

**Impact on prior conclusions:** §7 is corrected in both this file and the
synopsis. Nothing else is invalidated. §3.7's "a 200 is not signal" gains its
sharper sibling in §3.20 — the feed *did* carry signal, from two days ago.

**Not changed, deliberately:** nothing is wired yet, and the FRED key has not
been requested as a blocking item. Round 14 was run **before** asking Kabil for
a signup precisely so his time would not be spent on a host that might have
refused datacenter IPs the way Farside, Binance and CME all did. It did not
refuse, so the ask is now worth making — and that ordering is the reusable part.
The PM edition also stays unbuilt until the five clean mornings are measured;
probing cannot touch the delivery path, and building it can.

## rev 9 · 2026-09-13 · Google rendered a lost brief as 0% error
**Sections touched:** header, §2.1g (new), §3.19 (new), §5
**Type:** DATA + CORRECTION
**Evidence:** Apps Script Triggers page, screenshot 2026-09-13 — one trigger,
owner *Moi*, `Basé sur l'heure`, function `sendBrief`, deployment `Head`,
`Taux d'erreur 0%`, `Dernière exécution 13 sept. 2026, 09:20:11`. Against:
zero GitHub runs at 08:20Z on 13 Sep, and no email before the 13:38 manual
dispatch.

| Field | Was | Now |
|---|---|---|
| The daily 09:25 timer | ❓ assumed intact, unverified (rev 8, §5) | ✅ present, healthy, `sendBrief`, 0% errors |
| Trigger deployment mode | not known to be a variable | **`Head`** — runs newest saved code, so the re-paste is live with no further step. Had it been a pinned deployment, the paste would have changed nothing |
| Stale-copy diagnosis | inference from weekday/weekend pattern + the guard in the old source | **directly observed**: the timer ran at 09:20:11, returned cleanly, and produced no brief |
| What "0% error rate" means | read as a health signal | "nothing threw" — which on 13 Sep was true of a morning with no brief at all |

**Why:** Kabil opened the Triggers page to answer §5's last ❓ and the answer
carried more than the question. The row does not only prove the timer exists;
its *last run* timestamp is this morning's missing brief, recorded by Google as
a success.

**Impact on prior conclusions:** None reversed; one upgraded. Rev 7 called the
stale Google copy the cause and said so from inference. It is now measured.
§3.19 is added as the general form, because the shape recurs: rev 7's own §2.1d
error was also a *ran* being written down as a *delivered*.

**Not changed, deliberately:** the five-clean-mornings count still starts at
zero on Mon 14 Sep. Three proofs in one afternoon — v7 dispatching, the
detector staying silent, the timer intact — are three proofs about the
mechanism, and the measurement is about mornings. Nothing here shortens it.

## rev 8 · 2026-09-13 · The trigger is current again, and the detector stayed quiet
**Sections touched:** header, §2.1f (new), §5, §10
**Type:** DATA
**Evidence:** Apps Script execution log `Brief dispatched 16:26 LIS (trigger
v7).`; GitHub run #64 `2026-09-13T15:26:45Z` workflow_dispatch success; brief
delivered `15:27:01Z` reading `Cloud run — built 16:26 LIS.` followed
immediately by `## THE SETUP`, with no warning banner between them; run #61
(`trigger_version=6`) for the contrasting case.

| Field | Was | Now |
|---|---|---|
| Installed script version | 6 — the weekend-guard copy | **7**, reported by the script itself on every dispatch |
| The re-paste blocker | 🔴 open, §5's top item | ✅ closed the same day |
| Trigger-drift detector | fires correctly (proved with a forced mismatch) | **and stays silent correctly** — the case that decides whether it is worth having |
| Weekend delivery | none | expected; Sat 19 / Sun 20 Sep are the first real test |
| Daily 09:25 timer | assumed intact | ❓ still assumed. `testNow` proves the code, not the schedule |

**Why:** Kabil re-pasted within the hour. The close is worth its own revision
because rev 7's whole point was that a change *made* is not a change that
*works*, and writing "done" here without the dispatch timestamps would repeat
exactly the error rev 7 corrected.

**Impact on prior conclusions:** None reversed. §2.1d's corrected rows stand,
and the five-clean-mornings count still starts at zero — it begins Mon 14 Sep.

**Not changed, deliberately:** §5 keeps an open ❓ for the daily timer rather
than marking the trigger fully proved. Re-pasting code does not delete a
trigger and the handler name is unchanged, so it *should* be intact — but
"should" is the word this project has been burned by twice, and nobody has
looked at the Triggers page. Monday at 09:20 settles it at no cost, where
asserting it now would be another §3.17.

## rev 7 · 2026-09-13 · A delivered-vs-target table with a delivery that never happened
**Sections touched:** header, §1, §2.1, §2.1d, §2.1e (new), §3.16–§3.18 (new),
§4 D15 (new), §5, §6, §8, §10
**Type:** CORRECTION + DATA + DECISION
**Evidence:** Gmail `subject:"Market Brief"` 5–13 Sep — eight messages, none
dated 12 Sep, none on 13 Sep before 12:38 UTC. Actions `market-brief.yml` run
list — 12 Sep carries only run #59 (11:45Z, `skip_email` dry-run, job
103548387840); 13 Sep carries nothing before #60, dispatched by hand this
session and delivered 13:38 LIS. Live dry-run of `scripts/main.py` with the
state file rewound to 2026-09-11 printing both banners above THE SETUP.

| Field | Was | Now |
|---|---|---|
| Sat 2026-09-12 delivery | `09:20 LIS ✅` | **no brief was sent.** The row was false |
| Sun 2026-09-13 delivery | not yet recorded | missed at target; sent by hand at 13:38 LIS |
| Consecutive clean mornings | 4 of 5 | **3**, then a two-day gap. Counter restarts |
| Basis of §2.1d | run logs and intent | the inbox, which is where a delivery exists |
| Detection of a missing brief | none — six checks, none watching for absence | `health.missed_days`; the next brief names the days that did not arrive |
| Detection of a stale trigger | none | `SCRIPT_VERSION` on every dispatch, compared against `health.EXPECTED_TRIGGER_VERSION` |
| Day-over-day label | hard-coded `vs yesterday` in three places | derived from the state file's own date |
| Apps Script warning claim (`docs/trigger-setup.md`) | "an expired token announces itself rather than appearing as a week of silence" | true for a throw, **false for a clean exit** — which is the case that happened. Corrected, with what each check does and does not cover |
| §6 trigger line | "NOT YET INSTALLED" | installed 2026-09-08; stale since |

**Why:** Rev 6 changed the brief to seven days a week, wrote "Requires Kabil:
the Apps Script copy in his Google account still carries the old weekend guard
and must be re-pasted", and then recorded the following Saturday as delivered
at 09:20. Both statements are in the same commit. The prediction was right and
the record was written as if the fix had already happened.

**Impact on prior conclusions:** §2.1d is corrected, not extended — three of
its rows stand and one was false. D14 (seven days a week) is *unaffected in
code and never took effect in production*, which is a distinction this file had
collapsed. §2.1b still stands: the trigger does work, and did on all three
weekdays. Nothing about the scheduler diagnosis changes; this failure is
downstream of it.

**Not changed, deliberately:** the crons stay at `25 8`/`25 9` and D5 stands.
They would have delivered Sunday's brief late rather than never, and on a
weekend "late" is worth more than the argument for tightening them. The
detectors are also deliberately *silent under uncertainty* — no
`last_sent_date`, an unparseable one, or a dispatch carrying no version each
produce no claim at all rather than a guess. §12.4a cost two wrong verdicts to
learn that, and a delivery warning that cries wolf would be retired within a
week. And the subject line is untouched: a gap warning belongs in a brief that
arrived, and by then the inbox list has already done its job.

**Requires Kabil:** two minutes, once. Re-paste `trigger/apps-script.gs` into
Apps Script (`docs/trigger-setup.md` → *Re-pasting after the code changes*).
Until then there is no weekend brief, and Saturdays and Sundays fire only from
GitHub's late scheduler.

## rev 6 · 2026-09-12 · Seven days a week
**Sections touched:** §2.1d, §4 D14 (new), §7, §10
**Type:** DECISION
**Evidence:** Kabil, this session. Workflow crons `25 8 * * *` / `25 9 * * *`;
`sendBrief` weekend guard removed; new tests on 2026-09-13 (Sunday) and
2026-09-14 (Monday).

| Field | Was | Now |
|---|---|---|
| Schedule | weekdays, `* * 1-5` | every day |
| Apps Script `sendBrief` | exits at weekends | dispatches every day |
| Weekend rendering | n/a — no weekend brief existed | unchanged, and now tested: no cash open, no close, says the market is shut |
| Delivery record | 2 clean mornings | 4 |

**Why:** The weekday filter was inherited from the cash session, which the
brief was never only about.
**Impact on prior conclusions:** None. D5's two-slot DST logic is untouched —
it resolves which slot owns *today*, which has nothing to do with weekday.
**Not changed, deliberately:** weekend briefs still suppress the NYSE open and
close. Running seven days is not a reason to print two windows that will not
happen, and the failure mode worth guarding is a seven-day brief that forgets
which days have a session.
**Requires Kabil:** the Apps Script copy in his Google account still carries
the old weekend guard and must be re-pasted, or Saturday and Sunday will fire
only from GitHub's late scheduler.

## rev 5 · 2026-09-12 · FED PATH, and a second wrong verdict retracted
**Sections touched:** §4 D13, §12.2, §12.4a (new), §10
**Type:** DECISION + CORRECTION + DATA
**Evidence:** probe rounds 12–13; dry-run 103548387840 — `Target 3.50–3.75% ·
EFFR 3.63%`, `Hike 25bps 80% · Fed maintains rate 20%`, `CPI August 2026 ·
+0.40% m/m · +3.4% y/y`. CME: `403 — suspected web scraping activity`.

| Field | Was | Now |
|---|---|---|
| Fed-path odds | ⚫ EXCLUDED, "no free source" (D13, §12.2) | 🟢 LIVE via Kalshi, keyless |
| Basis of that verdict | CME FedWatch is a data-free iframe | true, and about CME's rendering, not the odds |
| Inflation prints | absent | CPI, core CPI, PPI from BLS, held until superseded |
| Policy rate | absent | target range + EFFR from the New York Fed |
| Wrong-verdict pattern | one instance (rev 4) | two, and §12.4a names the shape they share |

**Why:** Kabil asked for the inflation prints, the last decision, and cut-vs-
hike odds. Two were straightforward; the third had been written off, and the
write-off was wrong.
**Impact on prior conclusions:** D13 is partly retracted. Its other two
clauses are now unconfirmed rather than settled, since both were reasoned the
same way.
**Not changed, deliberately:** the brief does not forecast the market's
reaction to either decision, which was the fourth thing asked for. The
interpretation layer was removed to hold D2, and a forecast set in the same
typeface as a fetched number would undo D4. A test asserts the section makes
no such claim. Polymarket is also left un-wired despite the deeper book: its
per-month event slugs would need re-pointing every meeting, where Kalshi's
tickers generalise.

## rev 4 · 2026-09-10 · A $6bn announcement that was present and unreadable
**Sections touched:** §2.1d (new), §3.9–§3.13 (new, renumbered), §12.2, §12.4
(new), §10
**Type:** CORRECTION + DATA
**Evidence:** brief run 102797967158 (the failing line); probe rounds 10–11;
dry-runs 102862384592 (NameError), 102863173257 (wrong norm), 102864401381
(correct); [Treasury sb0607](https://home.treasury.gov/news/press-releases/sb0607).

| Field | Was | Now |
|---|---|---|
| Fiscal Data buybacks verdict | `S8` — "results only, no future-dated operations exist in the set" | `S0` — carries announced operations too. **The original claim was wrong** |
| Basis of that verdict | one filtered query on 2026-09-06 returning one row | re-tested; the single row meant nothing further had been announced *that day* |
| Announced operation rendering | identical to a completed one, blank amounts | leads the section, "⚠ ANNOUNCED — buyback TODAY", cap, Lisbon window, bucket-aware step-up |
| Step-up comparison | median across all maturity buckets | median within the bucket, ≥2 peers required, else no claim |
| Fetcher test coverage | none — fixtures only | `treasury_ops` run end to end with `_json` stubbed |

**Why:** The one operation Kabil explicitly asked to track had its most
significant change in months, and the brief rendered it as noise.
**Impact on prior conclusions:** §12.2's buyback row is corrected, and §12.4
adds the rule that produced the error — a negative verdict from a single
observation is not a property of a dataset. Nothing else is affected; the
Treasury-has-no-press-feed finding still stands and is unrelated.
**Not changed, deliberately:** the press-release index is still not scraped.
Round 10 found it server-rendered and therefore parseable, but the operations
API now carries everything the announcement did — cap, window, maturity range
— from a stable JSON endpoint. Adding a scraper for information already held
would be new breakage for no new information.

## rev 3 · 2026-09-08 · The trigger is installed. Phase changes.
**Sections touched:** header, §1, §2.1, §2.1b (new), §2.1c (new), §3.9 (new),
§4 D7, §5, §10
**Type:** DATA + DECISION
**Evidence:** Apps Script execution log `Brief dispatched 13:27 LIS.`; GitHub
run #44 `2026-09-08T12:27:42Z` workflow_dispatch success; Apps Script Triggers
page showing one time-based `sendBrief` trigger; scheduled run #42 job log
`A brief for 2026-09-07 was already sent; this scheduled run is a duplicate.`

| Field | Was | Now |
|---|---|---|
| Status | 🔴 Delivery timing unsolved | 🟢 Trigger installed · 🟡 awaiting measurement |
| §1 problem class | "a delivery problem… blocked on one person for one quarter of an hour" | "a measurement problem… blocked on nothing but five weekday mornings" |
| D7 | ✅ Accepted — not installed | ✅ Locked — installed and proven |
| Highest-value open item | install the trigger | five clean weekday mornings |
| Duplicate guard | written on theory (2026-09-05) | ✅ CONFIRMED in production (2026-09-07) |

**Why:** The item that had headed §5 since this file existed is done, and
leaving it there would misdirect the next session to work that no longer needs
doing.
**Impact on prior conclusions:** None invalidated. §1's diagnosis is vindicated
rather than overturned — the delay was GitHub's scheduler, and bypassing it
took the brief from 4.5 hours late to 15 seconds.
**Not changed, deliberately:** §2.1 still reads ❓ UNKNOWN for delivered-vs-
target. One dispatch at 13:27 on a Tuesday is not a week of 09:25 mornings, and
writing "solved" now would be exactly the error §9 warns about. The crons also
stay registered (D5 stands) — §2.1c just proved they cost nothing when the
trigger wins the race.

## rev 2 · 2026-09-07 · The scheduler failure, observed live
**Sections touched:** §2.1, §2.1a (new), §10
**Type:** DATA
**Evidence:** GitHub Actions API, 2026-09-07 10:22 UTC — zero scheduled runs
for `market-brief.yml` today; workflow `state: active`; last scheduled run
33878985519 at 2026-09-04 13:36 UTC. Kabil, this session.

| Field | Was | Now |
|---|---|---|
| Consecutive scheduled briefs late | 12 of 12 (📄 REPORTED) | 13 of 13, the 13th ✅ CONFIRMED |
| Direct observation of the failure | none — all latency reconstructed from timestamps after the fact | §2.1a, checked while it was happening |
| Manual dispatch latency | ✅ CONFIRMED sessions 6–7 | ✅ CONFIRMED again 2026-09-07, ~2 min to inbox |

**Why:** The first time the delay was caught in the act rather than measured
afterwards, and the first time it cost Kabil an actual morning. That deserves
a dated row rather than being folded into a median.
**Impact on prior conclusions:** None are invalidated — this is the predicted
behaviour, not a surprise. It strengthens §1 and §5: the diagnosis was right,
and the fix has been sitting uninstalled for two days.
**Not changed, deliberately:** the crons stay registered and §4 D5 stands. A
scheduler that is four hours late still beats no fallback at all, and once the
trigger is installed `last_sent_date` makes the late run exit silently — which
is exactly what will happen with today's run when it eventually starts.

## rev 1 · 2026-09-06 · Origin
**Sections touched:** all
**Type:** DATA + DECISION + STRUCTURE
**Evidence:** repo `kabil1101/Kab` @ `6d11ca5`+; Actions runs 33981684155
(token permissions), 33986074445 and 34032465219 (live briefs), probe rounds
1–9; sessions 1–7 of this conversation.

| Field | Was | Now |
|---|---|---|
| Project state file | none | this file, rev 1 |
| Source register | scattered across commit messages and README prose | §12.2, one table, nulls included |
| D8 token-scope claim | asserted from community reports | ❌ RETRACTED with the measurement that killed it |

**Why:** Seven sessions of decisions, retractions and dead sources existed only
in commit messages and chat scrollback. A new session had no single place to
read what had been tried and what had failed.
**Impact on prior conclusions:** N/A — origin.
**Not changed, deliberately:** the two cron entries stay registered even though
they have never delivered on time. They are the fallback behind the external
trigger, and `last_sent_date` already stops them sending a duplicate. Removing
them before the trigger is installed would leave no delivery path at all.

---

## §12 · THE SOURCE REGISTER

> ⚠ **THE FAILURE MODE OF THIS REGISTER IS BECOMING A LIST OF THE SOURCES THAT
> WORKED.** Three defences:
> 1. **Log every source tried, including the dead ones.** The dead entries are
>    the ones that stop the same API being re-attempted in six months.
> 2. **A verdict requires a probe from a runner.** Documentation, a browser
>    test, and community consensus are all 🔴 DOCUMENTED and nothing more.
> 3. **Record what the probe changed.** A probe that only confirmed what was
>    already assumed is a probe that was not needed; nine of nine changed a
>    design.

### §12.1 Taxonomy

| Code | Failure mode |
|---|---|
| `S0` | Works — wired and live-verified |
| `S1` | Datacenter or geographic block (403 / 451) |
| `S2` | Paid only, no free tier |
| `S3` | Endpoint does not exist (404), including ones long assumed to |
| `S4` | Field exists in the schema and is always null |
| `S5` | Answers 200 but the content is noise |
| `S6` | Client-side render — HTML contains no data |
| `S7` | Reachable, not yet parsed |
| `S8` | API limitation (unsupported filter, no forward records) |

### §12.2 The register

| Source | Code | Verdict | Evidence |
|---|---|---|---|
| ForexFactory `thisweek` | `S0` | 🟢 LIVE | calendar section, every run |
| Kraken ticker | `S0` | 🟢 LIVE | crypto section |
| alternative.me F&G | `S0` | 🟢 LIVE | sentiment section |
| CoinGecko global | `S0` | 🟢 LIVE | sentiment section |
| Yahoo chart API | `S0` | 🟢 LIVE | macro section; `^TNX` needs a /10 guard |
| Deribit ticker + book | `S0` | 🟢 LIVE | derivatives + options; single venue, labelled |
| TFTC ETF flows | `S0` | 🟢 LIVE | flows section; CC BY 4.0, attribution required |
| Federal Register documents | `S0` `S4` `S8` | 🟢 LIVE | prose extraction; `effective_on` null 21/21; `comments_close_on` not filterable (400) |
| Fed RSS (speech/testimony/monetary) | `S0` | 🟢 LIVE | POLICY DESK; CDATA-wrapped, BOM-prefixed |
| Fiscal Data buybacks | `S0` | 🟢 LIVE | announced AND completed operations; caps in `max_par_amt_redeemed`; values arrive as strings incl. `"null"` **(was: `S8`, "results only — no future-dated operations exist in the set" — ❌ WRONG, see §11 rev 4)** |
| TreasuryDirect upcoming | `S0` | 🟢 LIVE | coupon auction calendar |
| TreasuryDirect preliminary announcement XML | `S0` | 🟢 LIVE | `/instit/annceresult/press/preanre/{year}/{BBPA_*.xml}` — carries `maxParAmountRedeemed`, `announcementDTM`, operation window. Fallback for the cap |
| Farside ETF flows | `S1` | ⚫ EXCLUDED | 403 to datacenter IPs, three escalating header attempts |
| Binance futures | `S1` | ⚫ EXCLUDED | HTTP 451 from US runners |
| CoinGlass | `S2` | ⚫ EXCLUDED | no free tier, $29/mo |
| `ff_calendar_nextweek.json` | `S3` | ⚫ EXCLUDED | 404 always; **never existed**; called "broken" for three weeks |
| `treasurydirect /buybacks/announced` | `S3` | ⚫ EXCLUDED | 404 |
| `home.treasury.gov/rss/press.xml` | `S3` | ⚫ EXCLUDED | 404, as are the Drupal `/feed` paths |
| `home.treasury.gov/rss.xml` | `S5` | ⚫ EXCLUDED | 200 — careers pages, SSBCI FAQs |
| CME FedWatch | `S6` | ⚫ EXCLUDED | QuikStrike iframe, no probabilities in the page |
| coinglass / coinalyze / theblock pages | `S6` | ⚫ EXCLUDED | emit literal `0%` placeholders that read as data |
| bykaranteli ETF JSON | `S7` | 🟡 PROBED | 200; TFTC chosen instead |
| AAII sentiment | `S7` | 🟡 PROBED | reachable, not parsed |
| Kalshi `KXFEDDECISION` | `S0` | 🟢 LIVE | binary contracts per meeting, keyless read API, mid of book. **Prediction-market prices, not futures-implied — the two can disagree and the brief says which it is** |
| BLS public API v1 | `S0` | 🟢 LIVE | CPI, core CPI, PPI. No key. No calculations on the free tier, so m/m and y/y are computed from the index; `"-"` is a real value (2025 appropriations lapse) |
| New York Fed rates | `S0` ⚠ | 🟡 **DEMOTED 2026-09-18** | EFFR is correct and honestly stamped. **The TARGET RANGE rides on the same row and therefore inherits EFFR's one-business-day publication lag**, so it is stale for 1–2 days after every FOMC (§3.24). Needs a second source, or a cross-check against the FOMC statement the brief already fetches (was: 🟢 LIVE, "target range + EFFR from the desk that publishes them" — true of EFFR, false of the range's timeliness) |
| Polymarket gamma | `S7` | 🟡 PROBED | 200, and far more liquid than Kalshi on the September meeting ($20m/24h). Not wired: its event slugs are per-month strings, where Kalshi's tickers generalise |
| CME quote service | `S1` | ⚫ EXCLUDED | `403 — "This IP address is blocked due to suspected web scraping activity"`. Farside's lesson, third occurrence |
| ~~Fed-path odds (any free source)~~ | ~~`S2` `S6`~~ | ❌ **VERDICT WRONG** | was: "needs contract-level Fed Funds settlements". It needs a prediction market, which is free. See rev 5 |
| FRED (St. Louis Fed) | `S0` | 🟠 **WIRED-READY, method settled (round 16).** Ask with `output_type=4` and an **explicit** `realtime_start`/`realtime_end`; a first print whose `realtime_start` equals today published today. **Never** use `releases/dates` to decide publication and **never** rely on the default realtime window — both lie (§12.10) | ⬇ round 15 detail below |
| FRED — round 15 detail | `S0` | 🟠 shape question answered. `output_type=4` returns the initial release **with `realtime_start` = the publication date**, which is exactly what *"came in this morning"* needs. `series/release` maps a series to its publisher. See §12.9 for the one unresolved caution | ⬇ round 14 detail below |
| FRED — round 14 detail | `S0`* | 🟡 PROBED | `400 · "The value for variable api_key is not registered"` from a runner — **reachable; auth is the only barrier**. Probed with a deliberately invalid key so nobody signs up for a host that would have blocked us. **Needs a full `fredaccount.stlouisfed.org` login, not just an email** (was: "needs a free key" — understated; the key cannot be requested or viewed while logged out). Still free, still inside D2. **Scheduled outage Sat 2026-09-19 14:30–16:00 LIS**, now in `data/watchlist.txt` |
| ZeroHedge via Feedburner | `S0` | 🟡 PROBED | `200`, 25 items, all timestamped, newest 0.7h old. **Window only 21.6h** — marginal for a 24h look-back, ample for a 5h one. Carries political commentary alongside market stories; see §12.8 |
| `zerohedge.com/fullrss2.xml` | `S3` | ⚫ EXCLUDED | 404. Feedburner is the live path |
| `watcher.guru/news/feed` (= `/feed`) | `S5` | ⚫ EXCLUDED | `200`, well-formed, 10 items, all timestamped — and **newest item 41.9h old**, carrying equity stories on the crypto beat. The site feed does not carry what the X account posts. §3.20 |
| CNBC `combinedcms` top news | `S0` | 🟢 **BEST OF ROUND** | `200`, 30 items, all timestamped, newest 3.1h old, **54.8h window**. Real wire content — the Strait of Hormuz vessel strike was in it |
| **OKX `public/liquidation-orders`** | `S0` | 🟢 **PASS — round 18. THE FINDING.** `200`, **keyless**, rows carrying `sz`, `ts`, `posSide` and `bkPx`, plus `totalLoss`. Closes the largest gap between Kabil's framework and this system. **Not wired**; window and aggregation unexamined (§3.31) |
| ~~CoinGlass / "no free liquidation source"~~ | ~~`S2`~~ | ❌ **VERDICT WRONG — round 18** | was: "no free tier, $29/mo", carried since rev 1 and already marked *unconfirmed rather than settled*. **CoinGlass being paid was a property of that route, not of the world** (§12.4a, third occurrence) |
| Bybit v5 | `S1` | ⚫ **EXCLUDED — round 18** | `403 "The Amazon CloudFront distribution is configured to block access from your country"`. **Fourth geo/datacenter block** after Farside, Binance and CME |
| Bitget mix ticker | `S0` | 🟡 **PROBED — round 18** | `200` carrying `fundingRate` **and** `holdingAmount`. A second venue for the two figures DERIVATIVES currently labels "single venue". Not wired |
| `bitget /mix/market/liquidation-orders` | `S3` | ⚫ **EXCLUDED — round 18** | `404 {"code":"40404","msg":"Request URL NOT FOUND"}`. A guessed path, not a Bitget limitation |
| Coinalyze API | `S0`* | 🟡 **PROBED — round 18** | `401 "Invalid/Missing API key"` — auth is the only barrier, the FRED shape. D2-compatible. **Superseded by OKX, which needs no key.** Distinct from the coinalyze *pages*, which stay `S6` |
| Kalshi midterm series | `S8` | ⚫ **EXCLUDED — round 18** | `KXHOUSE`, `KXSENATE`, `KXMIDTERMS`, `KXHOUSECONTROL` all return `200 {"markets":[]}`. **An empty list at 200 is the quietest possible failure.** Discover the series, never guess the ticker |
| **`state.gov/rss-feed/…` (singular)** | `S0` | 🟡 **PROBED — round 18** | 20 feeds listed on the department's own index, including `press-releases`, `collected-department-releases` and the regional desks. **Round 17's exclusions were about URLs I invented**, not about State |
| `senate.gov hearings.xml` | `S0` | 🟡 **PROBED — round 18, verdict corrected** | Root `<css_meetings_scheduled>`, 19 × `<meeting>` with `date_iso_8601`, `time`, `committee`, `type`, `room`. Round 17 called it unreadable; that was my parser. ⚠ blank fields occur |
| **White House `presidential-actions/feed/`** | `S0` | 🟡 **PROBED — round 17** | `200`, `application/rss+xml`, 30 items, **30/30 dated**, newest 14.5h, 35-day window. **No datacenter block** — the round's flagged `S1` risk did not materialise. Not wired: the top three items were saltwater angling, hunting heritage and Senate withdrawals. Needs §3.6's two-tier word list before it renders |
| `state.gov/rss-feeds/press-releases/feed/` | `S5` | ⚫ **EXCLUDED — round 17** | `200` serving **`content-type: image/png`**, 663KB, at a feed URL. Not a feed by any reading |
| `state.gov/rss-feeds/secretary-of-state/feed/` | `S3` | ⚫ **EXCLUDED — round 17** | `404` (dressed as `application/rss+xml`, 156KB — a styled error page) |
| `state.gov/rss-feeds/` | `S7` | 🟡 **PROBED — round 17** | `200 text/html`, 172KB — the **index** of feeds, not a feed. The next round parses this page for real URLs instead of guessing a fourth time |
| **Kraken OHLC `interval=1440`** | `S0` | 🟢 **PASS — round 17** | `200`, **721 daily candles**. 14-day ADR **2.43%**, last close $77,994. Unblocks threshold v2 (D19) on a host already LIVE |
| **CoinGecko `/global` stablecoins** | `S0` | 🟢 **PASS — round 17** | `usdt 6.861`, `usdc 2.762`, alongside `btc` and `eth`, **in the call the brief already makes**. Supply derivable from `total_market_cap` in the same payload, which D24 requires |
| Polymarket gamma — filter honesty | `S8` | ⚫ **EXCLUDED — round 17** | `tag=fed` **silently ignored** and `closed=false` returned a market that closed 2026-06-01. A well-formed 200 answering a different question (§3.27). Kalshi generalises by ticker and needs no probe |
| Yahoo IBIT | `S7` ⚠ | ⚠ **INCONCLUSIVE — round 17** | `HTTP 429 · Too Many Requests`. The host never answered, so this is **not** a verdict on IBIT (§3.28) |
| Yahoo Brent `BZ=F` | `S7` ⚠ | ⚠ **INCONCLUSIVE — round 17** | `HTTP 429`, same call, same run |
| **Yahoo — host concentration** | ⚠ | 🔴 **RISK, logged not fixed** | Not a source: a **host**. Eleven shipping lines, no fallback on any, and round 17 drew a `429` from an Actions runner. §12.5 watches sources going quiet, not hosts becoming load-bearing (§3.28) |
| **CourtListener v4 search** | `S0` | 🟢 **PASS — round 17** | `200` **keyless**, 1,355 dockets / 40,456 documents for `OpenAI`, real cases by name with `dateFiled` ordering. Gives the 1 Oct watchlist entry a confirmation route it did not have |
| `senate.gov/.../hearings.xml` | `S7` | 🟡 **PROBED — round 17** | `200`, 23KB, `text/xml`. **The probe's own parser could not read it** — it looks for RSS `item`/Atom `entry` and the Senate uses its own schema. Reachable, not yet parsed; **not** a dead source |
| `docs.house.gov` calendar | `S6`? | 🟡 **PROBED — round 17** | `200`, 58KB HTML, **zero** occurrences of `hearing` or `markup`. Signature of a client-side render, as CME and Coinglass were. Provisional — confirm before excluding |
| MarketWatch top stories | `S5` | 🟡 PROBED | `200`, fresh (0.3h) but only **6.7h window** and the wrong beat — retail personal finance, not a market wire |
| Yahoo Finance news RSS | `S1` | ⚫ EXCLUDED | `429 Too Many Requests`. **And excluded on principle: Yahoo's chart API is the whole MACRO section** — §3.21 |
| financialjuice.com | `S6`? | 🟡 PROBED | `200` HTML, **no RSS/Atom link advertised**. The squawk is a real-time product, almost certainly client-rendered. Unresolved |
| X / Twitter API (any account) | `S2` | ⚫ EXCLUDED | Free tier killed for new developers 2026-02-06; pay-per-use at $0.005/read (~$23–60/mo for this use). Basic/Pro closed to new signups. Nitter under cease-and-desist. **Fails D2 and the reachability bar at once** |
| ETH ETF flows | — | ❓ | TFTC is Bitcoin-only; no free replacement found |

### §12.3 Promotion ladder

| 🔴 DOCUMENTED | 🟡 PROBED | 🟠 WIRED | 🟢 LIVE |
|---|---|---|---|
| Someone says it works. Counts for nothing | 200 from an Actions runner **and** its payload shape read | Fetcher written, degradation path tested, offline tests pass | Correct output observed in a real brief, with the run id recorded |

⚫ **EXCLUDED** — probed and failed, or paid. **Stop re-attempting it.** An
excluded entry is worth as much as a live one: it is what stops the same dead
API being rediscovered enthusiastically in six months.

### §12.8 What round 14 actually settled about the news idea

Kabil named four X accounts. Probed at their primary sources, the result
inverts the premise:

| His account | Primary source | Verdict |
|---|---|---|
| @zerohedge | Feedburner RSS | 🟡 the only one that survives as a direct relay |
| @WatcherGuru | watcher.guru RSS | ⚫ **42 hours stale and the wrong beat** |
| @financialjuice | no feed advertised | 🟡 unresolved, likely client-rendered |
| @DeItaone | a Bloomberg terminal | ⚫ no free primary, by design |

**CNBC — which he did not name — beat three of the four.** 30 items, a 54.8h
window, three hours fresh, and genuinely market-moving content in it.

The lesson is §12.4a pointing forward rather than backward: the accounts were
the *route* he knew, not the *fact* he wanted. Probing the fact found a better
route he had not thought to ask for.

**Still his to decide:** ZeroHedge mixes market stories with political
commentary. In a brief where every line is a fetched number with a source and
an age stamp, a commentary headline renders with identical authority. That is
§3.9 inverted — opinion typeset as data — and it would be the first unsourced
claim the brief has ever printed.

### §12.10 Round 16 — both cautions resolved, and the method is now a rule

Run 35030196370, job 104586657834.

**Q1 — the default realtime window is not today, and it moves.** Two calls
returned `2026-09-04`; round 15's two returned `2026-09-11` and `2026-09-15`.
**An explicit window is honoured exactly**: asking `realtime_start=2026-09-15&
realtime_end=2026-09-15` returned `2026-09-15`. So the rule is *name the window
on every call* and the default's wobble stops mattering. ✅

**Q2 — `releases/dates` lists SCHEDULED dates.** Asking for 2026-09-15 →
2027-01-13 returned 6 of a count of **2,965**. Worse, the FOMC release (id 101)
returns `2026-12-31, 12-30, 12-29, 12-28, 12-27, 12-26` — FRED projects a daily
release date for it through the end of the year. **A date from a calendar
endpoint is a plan, not an event.** ⛔ Never use it to claim publication.

**End-to-end, on a release that landed this morning.** Empire State published
08:30 ET today. Release 321 → series `AWCDINA066MNFRBNY` → initial releases:

```
{"realtime_start": "2026-09-15", "realtime_end": "9999-12-31", "date": "2026-09-01", "value": "14.9"}
{"realtime_start": "2026-08-17", ..., "date": "2026-08-01", "value": "8.2"}
{"realtime_start": "2026-07-15", ..., "date": "2026-07-01", "value": "6.0"}
```

`realtime_start` = **today** on the newest, and the mid-month cadence on the
two before it matches Empire State's real schedule. **The observation's own
vintage proves it published today — no calendar endpoint involved.**

**The method, settled:**

1. `output_type=4` with explicit `realtime_start=1776-07-04&realtime_end=9999-12-31`
2. read the newest observation's `realtime_start`
3. equals today → it published today, and the value is the first print

**Latency, measured:** the series carried `last_updated: 2026-09-15 07:33:29-05`
— 08:33 ET, about three minutes after an 08:30 ET release. A 14:00 Lisbon
(09:00 ET) edition will comfortably have the morning's print.

**Useful field found in passing:** `release_last_updated` on `releases/dates`
is a real timestamp, and it disagrees with `date` — *Coinbase Cryptocurrencies*
listed `date: 2026-09-15` with `release_last_updated: 2026-09-14 19:06:24-05`.
Further evidence that `date` is nominal.

### §12.9 Round 15 — FRED can carry "came in", with one caution

Run 35007629742, job 104511294765. Key redacted from every printed URL
(`api_key=***REDACTED***` throughout; the probe reads it from the environment
and never writes it to source).

| Question | Answer |
|---|---|
| Does a real key work? | ✅ `200`, PAYEMS 1,052 observations |
| Is the initial release retrievable? | ✅ `output_type=4` → `{"realtime_start": "2026-09-04", "realtime_end": "9999-12-31", "date": "2026-08-01", "value": "159075"}` |
| Is the **release date** available? | ✅ **`realtime_start` IS the publication date** — 4 Sep is exactly when August payrolls published |
| Which release publishes a series? | ✅ `series/release` → id 50, *Employment Situation*, `press_release: true` |
| What published on a given day? | ✅ `releases/dates` returns dated releases |

**The decisive test returned identical values — and that was the right answer,
not a failure.** August payrolls read 159,075 both as first published and
today. The probe's own verdict said this was ambiguous. It was not: the
initial release carries **`realtime_end: 9999-12-31`**, which means *this value
is still current and has never been revised*. The values agreeing carried no
information; **the field that resolved it was metadata, not the number** —
§3.22.

**⚠ Unresolved, and it must be settled before the PM edition trusts a release
date.** Two calls seconds apart returned different `realtime_start` values for
"today": the first said `2026-09-11`, the second `2026-09-15`. Neither request
set a realtime parameter, so both should have defaulted to today. Likely edge
caching. **If a cached four-day-old realtime window can be served, then
"is this today's print" cannot be decided from `realtime_start` alone.** One
more probe round before anything renders on it.

Also unresolved: `releases/dates` listed *"FOMC Press Release, 2026-09-15"* on
a day the FOMC decision is still **tomorrow**. Whether a listed date means
*published* or *scheduled* decides whether the PM edition can say "released
this morning" at all. Same round.

### §12.12 Round 18 — the liquidation question, answered in one call

| # | Target | Result |
|---|---|---|
| 1 | **OKX liquidation orders** | 🟢 **PASS, and the round's answer.** 200, keyless, `sz` + `ts` + `posSide`. §3.31 |
| 2 | Bybit | ⚫ **`S1`** — `403 "The Amazon CloudFront distribution is configured to block access from your country"`. **Fourth geo/datacenter block**, after Farside, Binance and CME |
| 3 | Bitget | 🟡 **half** — the ticker answers 200 with `fundingRate` *and* `holdingAmount`; the guessed `liquidation-orders` path is `404` |
| 4 | Coinalyze API | 🟡 **`401 "Invalid/Missing API key"`** — auth is the only barrier, the FRED shape. Free tier behind a free signup, so D2-compatible. **Now unnecessary: OKX needs no key at all** |
| 5 | Kalshi midterms | ❌ **FAIL, and it disproves a plan assumption** |
| 6 | State Department | 🟢 **SOLVED by reading instead of guessing** |
| 7 | Senate schema | 🟢 **SOLVED — and round 17's verdict was my parser's fault** |
| 8 | Yahoo ×3 | ⚠ **429 again — and the re-probe corrected §3.28 rather than confirming it** |

#### Bitget is a second venue for something the brief already labels

The ticker call that was only meant to prove the host answers came back with
`fundingRate: 0.000016` and `holdingAmount: 33649.42`. DERIVATIVES currently
prints Deribit funding and OI with the honest caveat *"single venue"*. **A
second venue is now one already-verified call away** — not wired, not
probed for shape beyond this one response, but no longer hypothetical.

#### Kalshi: the plan said it needed no probe. It does.

`docs/BUILD_PLAN.md` §9: *"Kalshi needs no probe — already LIVE and
keyless."* True of `KXFEDDECISION`. All four guessed midterm series —
`KXHOUSE`, `KXSENATE`, `KXMIDTERMS`, `KXHOUSECONTROL` — returned
`200 {"cursor":"","markets":[]}`.

**An empty list at 200 is the quietest possible failure**: no error, no 404,
nothing to catch. A fetcher written on the plan's assumption would have
printed an empty midterm block every morning and nobody would have known
whether that meant *no markets* or *wrong ticker*. The series must be
discovered from Kalshi's own series endpoint, not guessed.

#### State: the guess was one character out

Round 17 tried `state.gov/rss-feeds/press-releases/feed/` and got a `200`
serving a PNG. The index lists **`rss-feed`** — singular:

```
https://www.state.gov/rss-feed/press-releases/feed/
https://www.state.gov/rss-feed/collected-department-releases/feed/
https://www.state.gov/rss-feed/near-east/feed/          (+ 17 more)
```

Twenty feeds, including regional desks. **Rubio is trackable after all**, and
round 17's `⚫ EXCLUDED` verdicts were about URLs I invented rather than about
the State Department.

#### Senate: the schema, and why round 17 could not read it

```
root <css_meetings_scheduled> · 19 × <meeting>
  cmte_code · committee · type · date · date_iso_8601 · day_of_week
  · time · room · AssociatedDocument
```

Not RSS, not Atom. Round 17's parser looked for `item`/`entry` and found
neither, then reported *"no items parsed"* — which reads as a dead source and
was a bug in my code. `date_iso_8601` and `time` are exactly what a forward
calendar needs. ⚠ One caution for whoever wires it: **the first record came
back with `committee`, `type` and `room` all empty**, so the fetcher must
tolerate blank fields rather than assume a well-formed record.

### §12.11 Round 17 — nine targets, one dispatch, and two findings nobody asked for

Run 2026-09-18, job 105590900580, five seconds wall clock. The batching worked:
one commit, one dispatch, one log read for nine questions.

| # | Target | Result |
|---|---|---|
| 1 | **White House `presidential-actions/feed/`** | ✅ **PASS** — 200, 30 items, **30/30 dated**, newest 14.5h, 35-day window |
| 2 | State Dept | ❌ **FAIL** — no readable feed at any of three guessed URLs |
| 3 | **Kraken daily OHLC** | ✅ **PASS, beyond the test** — 200, **721 candles** (asked for ≥20) |
| 4 | Polymarket | ❌ **FAIL, and instructively** — §3.27 |
| 5 | **CoinGecko stablecoins** | ✅ **PASS, zero cost** — `usdt 6.861`, `usdc 2.762` already in the call the brief makes |
| 6 | Yahoo IBIT | ⚠ **INCONCLUSIVE** — 429, host never answered. §3.28 |
| 7 | Yahoo Brent | ⚠ **INCONCLUSIVE** — 429, same |
| 8 | **CourtListener** | ✅ **PASS** — 200 keyless, 1,355 dockets, real cases by name |
| 9 | Senate / House calendars | ⚠ **INCONCLUSIVE** — see the probe bug below |

#### The number that matters most: 2.43%

Kraken's 14-day **average daily range on BTC is 2.43%**, last close $77,994.

The PM edition's v1 threshold (D19) is a flat **±1.0%**, chosen because nothing
better existed. Against today's range that is **41% of an average day** — and
the plan's own proposed v2 rule was *"moved more than 40% of average daily
range"*.

**So the guess was almost exactly right, and that is the point.** It is right
by coincidence, in this regime, this fortnight. At 60 vol the same ±1.0% is a
shrug; at 15 vol it fires twice a day. **Threshold v2 is now unblocked and can
be measured rather than argued**, which is what D19 gated it on — and it costs
no new host, because Kraken has been LIVE since August.

#### The White House feed passes on mechanics and is not yet useful

30 items, every one dated, newest 14.5 hours, 35 days of window. **Government
hosts did not block the datacenter IP** — the round's flagged `S1` risk, which
sank Farside, Binance and CME, did not materialise here.

But this probe's own instruction was *read the samples, not the status codes*,
and the top three read:

```
· [14.5h] RESTORING AMERICAN SALTWATER ANGLING AND RECREATION
· [14.5h] Reinvigorating America's Hunting Heritage
· [20.2h] Withdrawals Sent to the Senate
```

**Two of the three are irrelevant to any market.** The feed carries what a
president signs, and most of what a president signs is not tradeable. That is
not a failure — it is exactly the condition §3.6 already solved once, when
`"trade"` matched `"Trademark"` and a marine-mammal permit reached a live
brief. **It wires with the same two-tier word list the Federal Register uses,
or it does not wire at all.** Promoted to 🟡 PROBED, not 🟠 WIRED.

#### My own probe had a bug, and the Senate is not dead

Target 9 printed *"200, but no items parsed"* for
`senate.gov/general/committee_schedules/hearings.xml` — 200, 23KB, `text/xml`.

**The source answered. My parser did not read it.** `_items()` looks for
elements named `item` or `entry`, which is RSS and Atom; the Senate publishes
its own schema, so nothing matched. Recording this as a dead source would have
been a wrong verdict caused by my code, and §12.4a is the standing warning
about exactly that.

**Correct verdict: `S7` — reachable, not yet parsed.** One more look at the
element names settles it.

The House side is a different story: `docs.house.gov` answered 200 with 58KB of
HTML containing **zero** occurrences of `hearing` or `markup`, which is the
signature of a client-side render — CME's failure and Coinglass's. Provisional
`S6`, and a second look should confirm it rather than assume it.

#### What the round changes

- **Unblocked:** threshold v2 (target 3), stablecoin lines at zero cost
  (target 5), the OpenAI watchlist date's confirmation route (target 8).
- **Still blocked:** Rubio is tracked by nothing. Both remaining policy
  primaries (State, Congress) need another round.
- **Newly at risk:** eleven live lines on one rate-limiting host (§3.28).
- **Newly harder:** Polymarket, which now needs a probe proving a filter is
  honoured rather than accepted (§3.27).

### §12.4a The shape both wrong verdicts share

Two register entries have now been wrong, and they failed the same way:

| Entry | What was observed | What was recorded |
|---|---|---|
| Fiscal Data buybacks | one query, one day, one row | "the dataset holds results only" |
| Fed-path odds | CME's page carries no data | "the odds have no free source" |

**Both mistook a property of one route for a property of the world.** The
observation was correct each time; the generalisation was not. Before writing
"unavailable", name the specific thing that failed and ask whether anything
else could carry the same fact.

### §12.4 A verdict is a claim, and claims decay

`S8` on the buyback set came from one query on one day and was recorded as a
property of the dataset. It was a property of that morning. **A negative
verdict drawn from a single observation gets re-tested before anything is
built on it** — the positive ones already require a probe, and this is the
same rule pointing the other way.

### §12.5 Kill criterion

A 🟢 LIVE source that renders `unavailable` in **three consecutive briefs** is
demoted to 🟡 and re-probed before anything is rewritten against it. Farside sat
at `unavailable` for twelve days before anyone checked why; that is the
behaviour this criterion exists to prevent.

### §12.6 The uncomfortable consequence

The bar in §12.3 means a new section costs three to nine probe rounds before a
line of fetcher is written, and each round is a commit, a dispatch and a log
read. That is slow, and it is the reason the sections that exist are correct.
It is also why the comfortable-work trap in §8 bites so hard: this process is
genuinely satisfying and it is not the bottleneck. **The bottleneck is a Google
consent screen.**

### §12.7 Toward a complete system

```
1. Trigger installed              -> brief arrives on time          [BLOCKED ON KABIL]
2. One week of delivered-vs-target -> timing declared solved or not
3. Watchlist populated with the events he actually trades
4. Only then: new sources, and only through §12.3
```

*A longer brief is an output of a brief that arrives, not a substitute for one.*

---

## §13 · HANDOFF — 2026-09-18

Four documents now. Read them in this order:

| | |
|---|---|
| `PROJECT_STATE.md` | this file — what is true, what is decided, what is open |
| `docs/BUILD_PLAN.md` | what to build. **Read its preamble first**, then its §9 |
| `docs/SYNOPSIS.md` | the story — how it got here and what went wrong |
| `data/watchlist.txt` | the dated events the brief counts down to |

### Read these four things first

1. **§3.26 — the token expires 2026-11-07 and nothing detects the failure.**
   Dispatch dies, the old cron fires hours later, the brief still arrives, and
   both detectors stay green while the project slides back to the 4.5-hour
   delay it spent three weeks solving. **The fix is a build-time-vs-target
   banner in `health.py`.** No probe, no new source, no schema change.
2. **§3.24 — FED PATH prints a target range that is stale for 1–2 days after
   every FOMC.** In the shipping brief. **Next occurrence 28 October.** The
   plan renames the section to EXPECTATIONS; that does not fix it. Fold the fix
   into Commit 1, which rewrites the section anyway.
3. **§3.25 — a scheduled task outside this repository, able to send mail, stops
   being dormant on 26 October.** That is inside the plan's own fragile
   fortnight, and the plan does not know it exists.
4. **§2.1h — delivery is solved, 5 of 5. Gate 0 is cleared.** Do not re-measure
   it. `docs/BUILD_PLAN.md` still says "3 of 5" because it was written the day
   before the fifth.

### The revised build order

The plan's §9 is sound and Gate 0 no longer blocks it. Two changes:

| | What | Why it moved |
|---|---|---|
| ~~1~~ | ~~`health.py` latency banner (§3.26)~~ | ✅ **DONE 2026-09-18, proven live on run #78.** §2.5 |
| ~~2~~ | ~~The batched probe round — 9 targets, 1 dispatch~~ | ✅ **RUN 2026-09-18.** Four passes, two failures, three inconclusive, two findings nobody asked for. §12.11 |
| ~~3~~ | ~~Commit 1 — three tiers — with the §3.24 fix in it~~ | ✅ **DONE 2026-09-18.** 381 checks |
| ~~4~~ | ~~Commit 2 — the zero-cost data lines~~ | ✅ **DONE 2026-09-18.** 409 checks |
| ~~5~~ | ~~Commit 3 — probed sources wired~~ | ✅ **DONE 2026-09-18.** BACKDROP and NEWS, live on run #86 |
| ~~6~~ | ~~Commit 4 — the PM edition and the state bundle~~ | ✅ **DONE 2026-09-18.** 475 checks, D21 proven live |
| **7** | **Commit 5 — timing and health** | **Last one, and it needs Kabil**: the PM's two Apps Script timers, a `SCRIPT_VERSION` bump to 8 and a re-paste. Until then the PM edition exists and nothing dispatches it |
| **8** | **Wire OKX liquidations** | Not in the original plan, and arguably ahead of everything left in it (§3.31) |

| — | **Probe round 18** | Still owed: the White House word filter, State's real feed URLs, the Senate schema, the two Yahoo `429`s, Kalshi's midterm tickers, and — if the addendum closes — CME futures and the unprobed liquidation APIs |
| — | ~~Renew the trigger token, late October~~ | **Not a commit — an action only Kabil can take**, and it must happen before 25 Oct |

### The fragile fortnight, now with four entries

| Date | Event | Effect |
|---|---|---|
| **25 Oct** | Portugal falls back | Lisbon–NY gap 5h → 4h; a Lisbon-anchored trigger lands an hour wrong |
| **26 Oct** | **§3.25's task stops being dormant** | **Added here — the plan does not have this row.** A second, mail-capable sender wakes inside the same window |
| **28 Oct** | **FOMC** | **Added here.** §3.24 fires again unless fixed |
| **1 Nov** | US falls back | Gap returns to 5h, desync closes |
| **3 Nov** | US midterms | Highest-volatility political event of the year |
| **7 Nov** | Trigger token expires | Dispatch dies — silently, until §3.26 is fixed |

**Five dated events in fourteen days, three of them new since the plan was
written.** The plan's own advice — renew the token in late October so the
fortnight contains no scheduled maintenance — is right and now more so.

### Decisions still owed by Kabil

1. **The 26 October task (§3.25)** — rewrite as an alarm, disable, or leave.
   Recommendation: rewrite as an alarm. Before the 25th.
2. **His manual morning checks** — what he looks at daily that the brief does
   not carry. Raised in the planning chat, unanswered. **The cheap wins are
   close to exhausted; this is where the remaining value is.**
3. **The rest of the events he trades around.** Four now exist. Still the least
   complete item in the file, open since rev 1.
4. **Any Fed speaker beyond Warsh**, by name.

### What is armed, and what is not

No check-in is scheduled into the chat being closed. The only live scheduled
thing touching this project outside GitHub Actions is §3.25's task. **The brief
itself needs no chat to run:** Apps Script dispatches it, Actions builds it,
Gmail delivers it, and none of that depends on a conversation being open.

### The discipline, restated because it is about to be tested

Everything in `docs/BUILD_PLAN.md` was designed in one chat and **none of it is
built.** Gate 0 existed to stop planning outrunning evidence, and it has now
cleared — which removes the excuse, not the discipline. Nothing marked 🔴
enters code until a runner answers a probe (§12.3). The plan adds nine
unprobed targets and every URL in four of them is pattern-matched rather than
verified.

> The section count is not the metric. The arrival time is.

---

**Standing instruction.** At the end of every session on this project: update
§1 if the phase changed, §2 with any new measurement, §4 with decisions and
retractions, §5 with what opened or closed, §10 with the session, §12.2 with
every source tried including the dead ones — then write the §11 entry, increment
the revision, and update the header date.
