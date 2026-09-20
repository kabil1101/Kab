# HANDOFF — DAILY MARKET BRIEF

*Written 2026-09-20 for the next chat. Read this first, then
[`PROJECT_STATE.md`](../PROJECT_STATE.md) in full — it is long by design and
§3 (findings), §4 (decisions), §5 (open questions) and §12 (the source
register) are the parts that stop you repeating work.*

---

## 0 · Read this before you touch anything

**Kabil is not a coder.** He is a crypto trader. He reads the brief, not the
repository. Explain in plain words; never hand him a diff and call it an
answer.

**Three rules that have each been learned the expensive way:**

| | |
|---|---|
| ⛔ **Nothing is working until a runner says so** | Seven defects were found between 18 and 20 Sep. **Not one was caught by the test suite.** Every one was found by dispatching a run and reading the output. Dispatch `market-brief.yml` with `skip_email: true` and read the log. |
| ⛔ **A green suite is evidence about the fixtures, not about production** | Twice the fixture and the code agreed and both were wrong about the world. Once a test asserted a config string was *present* while the string did nothing, and the whole PM fallback was dead for a day. |
| ⛔ **Probe before you wire, and record the rejections** | `scripts/probe.py` is rewritten each round and the verdicts live in §12.2. A rejected source is worth as much as an accepted one — without the record the next person re-probes FinancialJuice and finds the same 404. |

---

## 1 · What it is, in one screen

Two editions a day, built on GitHub Actions, emailed to `kabil.dh@gmail.com`.
No laptop involved. 21 live sources. Zero cost.

| | Lands | Anchored to | Shape |
|---|---|---|---|
| **Morning** | 09:25 Lisbon, 7 days | a Lisbon hour | full picture, three tiers |
| **PM** | 08:00 New York (13:00 Lisbon most weeks) | **New York** | a delta against the morning |

**Morning, in tiers:** Tier 1 `CLOCKS · THE SETUP · TODAY · CYCLE` — Tier 2
`CRYPTO · FLOWS · DERIVATIVES · SENTIMENT · MACRO & EQUITIES` — Tier 3
`AHEAD · EXPECTATIONS · POLICY DESK · BACKDROP · NEWS`.

**PM:** a fixed spine (BTC/ETH since 09:20, cross-asset, what is still dated
today) plus a `MATERIAL CHANGE` body that prints only what crossed a
threshold. Most afternoons it says *"No material change since 09:20"* — that
is a real answer, not an empty section. **At weekends it runs crypto only**
(D25).

### Delivery chain

```
Google Apps Script timer (v8)          trigger/apps-script.gs
        │  workflow_dispatch + trigger_version + edition
        ▼
GitHub Actions  market-brief.yml       4 cron slots as FALLBACK ONLY
        │  25 8 / 25 9 UTC  (morning, DST pair)
        │   0 12 /  0 13 UTC  (PM, DST pair)
        ▼
scripts/main.py → gather (lazy) → render → Gmail SMTP → state commit
```

**Why the pairs:** GitHub cron is UTC-only and Lisbon shifts. Exactly one slot
in each pair maps to the target hour, and the job resolves which from *the cron
expression that fired*, never the wall clock — a late start must not drop the
brief.

**Why the PM is anchored to New York:** the Lisbon–NY gap is 4, 5 or 6 hours
depending on the week. Anything anchored to a Lisbon hour is wrong for about
two weeks a year, in both DST mismatch windows.

---

## 2 · The file map

| File | What it is |
|---|---|
| `scripts/main.py` | orchestration, run guards, the lazy context, SMTP, state write |
| `scripts/sources.py` | every fetcher. All raise; the caller degrades |
| `scripts/render.py` | both editions, markdown + HTML |
| `scripts/state.py` | the state bundle, 30-day history, the AM baseline |
| `scripts/health.py` | **the only module that checks the system, not the market** |
| `scripts/cycles.py` | expiries, holidays, rolls — derived, never fetched |
| `scripts/watchlist.py` | the hand-curated radar parser |
| `scripts/probe.py` | rewritten each round; touches nothing the brief uses |
| `data/watchlist.txt` | 7 fields: `date \| tag \| event \| url \| verified \| class \| lead` |
| `state/latest.json` | the day-over-day baseline **and** `am.at` |
| `state/shadow.jsonl` | D20 — what the PM body *would* have printed |
| `tests/test_brief.py` | 643 checks, offline, 0.2s |

---

## 3 · The rules the brief obeys

These are not style preferences. Each cost something to learn.

| | |
|---|---|
| **D1** | The recipient is a module constant. No cc, no bcc, not overridable by env, input, or fetched content |
| **D2** | Zero cost. A free tier behind a free key qualifies; a trial that converts does not |
| **D3 / D9 / D22** | **No buy/sell calls, no price targets, no position sizing, no level flagging, no interpretation.** The brief carries numbers and their age. The reading is Kabil's |
| **D16** | Commentary is visibly marked as commentary. An opinion headline typeset like a wire item is an opinion wearing a fetched number's clothes |
| **D21** | A missing morning baseline suppresses PM deltas **entirely** — never fall back to yesterday's close |
| **D24** | Stablecoins print supply *and* dominance together. Dominance is a ratio; it rises when the denominator falls |
| **D25** | The weekend PM edition is crypto only, and "shut" is decided by **the quotes' own timestamps**, never by `weekday() >= 5` |
| **§3.9** | *Present, sourced, correctly stamped, and materially misleading.* Met **six times**. It is the failure mode of this project |
| **§12.4a** | A verdict is a claim, and claims decay. Absence of evidence is not evidence |

**Honest degradation, everywhere:** every fetcher raises, every section prints
`unavailable — <reason>`, and **empty is never the same as failed**. A section
that is quiet says why.

---

## 4 · What just happened, and the mistake worth studying

On 20 Sep Kabil asked whether the brief watches four accounts he follows
(@DeItaone, @zerohedge, @financialjuice, @WatcherGuru). It watched one, through
its website — X costs $0.005 a read with no free tier and Nitter is under
cease-and-desist. He then asked for **headlines in both editions**.

Two probe rounds chose sources on **cadence** — items per hour — because the PM
window is short and a slow feed would be empty most afternoons. Four feeds were
wired, a PM news section was built on a delta window, and it shipped.

He killed it the same day: *"it is not what i asked for, i don't need headlines
that doesn't have relation with the markets and politics."*

**The mistake was the metric, not the noise.** Every account he named is
curated for *relevance* — that is the whole reason he named them — and
relevance was never a criterion in either round. It appeared only as a defect
to filter afterwards, three times, each time patching the symptom: baseball,
then Reuters ticker landing pages, then Harry and Meghan.

Round 22 said so out loud and it was misread. `site:reuters.com/markets` scored
**best of five on cadence** while returning pages carrying no story at all.

> **A metric that rates content-free pages as the top source is not a metric
> with a scoping problem.**

Reverted byte-identical. §3.39 records the reversal rather than deleting it.

**If this is ever rebuilt, the order has to invert:** agree with Kabil what
belongs in the section *first*, then find sources that match it, with cadence
as a tiebreak. **Neither round asked him.** That was the hole, and it is the
same hole as open question 1 below.

---

## 5 · Open, in priority order

| # | Item | Why it matters |
|---|---|---|
| **1** | **What does Kabil check every morning that the brief still does not carry?** Asked in the planning chat, never answered | **This is where the remaining value is.** The easy additions are exhausted, and §3.39 is what happens when this gets answered by inference instead. **Ask him. Do not infer.** |
| 2 | The curated half of the radar is empty of everything he has not named | Owed since day one. Only he knows the events he trades around |
| 3 | The shadow log needs ~2 weeks of real PM editions | Until then v1's fixed thresholds cannot be replaced with range-scaled ones. It has **one** honest row |
| 4 | OKX contract multiplier unprobed | So liquidations print counts and side skew, and **no dollar figure**. `sz` is in contracts; `sz × bkPx` overstates ETH tenfold |
| 5 | State Dept feeds (20 real URLs known), White House feed needs §3.6's two-tier word list | Both documented, neither wired |
| 6 | ZeroHedge signal-to-noise | §3.30 — Kabil's call, not a technical one |

**Dated and unavoidable: 7 November — the GitHub trigger token expires.** When
it dies the whole chain goes silent: dispatch fails, no brief at 09:20, the
cron fallback picks it up hours later, and the brief still *arrives*. `health.py`
is what catches that. The brief counts down to it in `data/watchlist.txt`.

---

## 6 · How to work with him

- **Brutal honesty, evidence-backed.** He spots filler. Praise must be specific
  or it reads as noise.
- **Format every update:** 1. What happened · 2. What it means · 3. What is
  risky · 4. My recommendation · 5. Next prompt / next action.
- **Separate proven facts from guesses from what still needs testing.** He asks
  for this explicitly and it has caught real errors — twice in this session a
  finding turned out to be a test artifact, not a production fault.
- **Simple words. Short sentences.** Explain a technical term the first time.
- **Challenge suboptimal ideas.** He wants the systematically best approach,
  not the convenient one, and says so.
- **Own errors loudly.** A retracted recommendation with the data that killed
  it is worth more than one quietly dropped. This file contains several.

**The comfortable-work trap in this domain:** *adding another section.* It is
engaging, it is visibly productive, and it is what to do instead of asking
Kabil the one question in open item 1. §3.39 cost a day to that trap.

---

## 7 · Before you finish any session

1. Run the suite — `python tests/test_brief.py`. 643 checks, offline, ~0.2s.
2. **Dispatch a run and read the output.** `skip_email: true`. The suite will
   not catch what you broke.
3. Update `PROJECT_STATE.md`: the finding in §3, the register in §12.2, the
   session in §10, and the change-log entry in §11 with **the evidence line and
   "Impact on prior conclusions"**. A change with no evidence line is not a
   valid change.
4. Push to `claude/daily-market-brief-kvfi35` **and** mirror to
   `claude/peaceful-carson-zc9vv3`.
5. Never commit a model identifier into the repository.

---

## 8 · Verifying the chain is alive

| Check | Where | What good looks like |
|---|---|---|
| Google is on v8 | any run's env block | `TRIGGER_VERSION: 8` |
| The morning fired on time | run event + time | `workflow_dispatch` near 08:2x UTC, no `BRIEF LATE` banner |
| The PM fired on time | run event + time | `workflow_dispatch` at 12:00Z (13:00 Lisbon), no banner |
| It actually sent | the log | `Sent to ***` then a state commit |
| The PM left the baseline alone | the log | `PM marker written; the daily baseline is untouched.` |

**A `state file unreadable (JSONDecodeError)` warning on every run is the test
suite's own corrupt-file test proving honest degradation. It is not a
production fault.** It was nearly reported as one.
