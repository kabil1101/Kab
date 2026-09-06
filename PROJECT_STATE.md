# PROJECT STATE — DAILY MARKET BRIEF

| | |
|---|---|
| **Project** | Daily Market Brief — automated pre-market brief, cloud-built, emailed |
| **Owner** | Kabil Dahmen |
| **Repo** | `kabil1101/Kab` · branch `claude/daily-market-brief-kvfi35` (default) |
| **Session 1** | 2026-08-21 |
| **Status** | 🟢 Content complete and live-verified · 🔴 Delivery timing unsolved |
| **Last updated** | 2026-09-06 |
| **Revision** | 1 |

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

The brief builds itself in GitHub Actions every weekday, fetches nine live
sources, renders markdown and HTML, and emails `kabil.dh@gmail.com` over Gmail
SMTP. It runs with the laptop shut. Content is complete: calendar, a forward
policy radar with countdowns, a policy desk tracking Warsh and Treasury
operations, crypto, ETF flows, derivatives, sentiment, macro and risk windows.
Nine sections, all live-verified in a real run, all degrading to a named
`unavailable` rather than a fabricated number.

**The diagnosis.** Everything that was ever wrong with the *content* has been
fixed and tested. What has never been fixed is *when it arrives*: across twelve
consecutive briefs the scheduled run started between 39 minutes and 11h49m
late, median about 4.5 hours. That delay is GitHub's scheduler queueing the job
before any of this code executes, so no amount of work inside the repository
can shorten it. The fix — an external timer that calls the dispatch API, which
starts within seconds — has been written, documented and committed since
2026-09-05 and is **not installed**, because installing it requires fifteen
minutes of Kabil's clicking that has not happened yet.
**This is a delivery problem, not a content problem, and it is blocked on one
person for one quarter of an hour.**

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
| Consecutive scheduled briefs that arrived late | 12 of 12 | 📄 REPORTED (Actions run history, sessions 1–4) |
| Best | 39 min late | 📄 REPORTED |
| Median | ~4.5 h late | 📄 REPORTED |
| Worst | 11 h 49 m late | 📄 REPORTED |
| Manual dispatch latency | seconds | ✅ CONFIRMED (every dispatch this session) |
| Target | 09:25 Europe/Lisbon | — |
| **Delivered-vs-target over a full week with the fix installed** | ❓ UNKNOWN | **the measurement that decides whether this is solved** |

The 39-minute figure is the trap: the schedule was near-punctual on its first
two days and then degraded. **One good morning proves nothing.**

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

**§3.9 — Positive: degradation is honest throughout.** Every fetcher raises
rather than returning a placeholder, every section prints `unavailable —
<reason>`, and an empty result is rendered differently from a failed fetch.
The brief has never printed a fabricated number. *Evidence: the "every source
down" test; the CoinGlass `0%` placeholder trap, avoided by quarantine.*

**§3.10 — Positive: Kabil rejects paid options consistently.** Zero-cost was
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
| D6 | Quarantine list — never fetch or cite: `deribit.com/statistics/*`, `optioncharts.io`, CME FedWatch, `coinglass.com`, `theblock.co/data`, `coinalyze.net` | ✅ Locked |
| D7 | Google Apps Script as the external trigger, not cron-job.org | ✅ Accepted — **not installed** |
| D8 | ~~The trigger token needs `Contents: write` and is therefore equivalent to the Gmail app password, so a third-party scheduler is unsafe~~ | ❌ **RETRACTED 2026-09-05.** Measured: the endpoint wants `Actions: write` and *refuses* `Contents: write` (§2.2). The claim came from community reports, not evidence. D7 still stands, but on convenience grounds — no new account — not security ones. cron-job.org was excluded on a false premise |
| D9 | No LLM analysis layer. Built, then reverted, to hold D2 | ✅ Accepted — consequence: the brief reports data, it does not interpret it |
| D10 | Curated watchlist is pipe-delimited plain text, not YAML — indentation must not be able to break it | ✅ Locked |
| D11 | Watchlist entries carry a last-confirmed date; >75 days prints as `unconfirmed` | ✅ Locked |
| D12 | Bessent tracked through operations (buybacks, auctions, refunding), not remarks, because Treasury publishes no usable feed — and the brief states the gap | ✅ Accepted |
| D13 | ETH ETF flows, aggregate liquidations and Fed-path odds stay out of scope. No free source. Saying so beats a permanent "unavailable" | ✅ Accepted |

---

## §5 · OPEN QUESTIONS

### Blocking / high value
- ⏳ **THE SINGLE HIGHEST-VALUE OPEN ITEM: install the Apps Script trigger.**
  ~15 minutes, walkthrough written at `docs/trigger-setup.md`. Until this is
  done the brief is a lunchtime brief. Everything else in this file is
  secondary to it.
- ⏳ Measure delivered-vs-target across a full week afterwards (§2.1).

### Mechanics
- ⏳ FOMC dates in the watchlist (16 Sep, 28 Oct, 9 Dec) came from secondary
  sources. One click on the Fed calendar link confirms or kills them.
- ⏳ The 2026-11-04 quarterly refunding date is the conventional
  first-Wednesday slot, **not** a published announcement. Marked `CONFIRM` in
  the brief text itself.
- ❓ Does the policy radar surface anything on a quiet week? Two live runs both
  produced the same four entries. Needs a month of observation.

### Process
- ❓ Is the AHEAD horizon (130 days) right? Untested against Kabil's actual
  planning window.

### Data Kabil still owes
- ⏳ **The events he already watches.** Summits, court dates, deal deadlines he
  is trading around. The curated leg of the radar is empty of everything he has
  not named, and only he knows that list.
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
  sources.py    (921)      one adapter per source; each raises or returns real data
  render.py     (849)      markdown + HTML; every unavailability handled explicitly
  main.py       (218)      run guard, orchestration, SMTP, recipient lock
  state.py      (102)      day-over-day memory + duplicate-send guard
  watchlist.py   (98)      the curated half of the policy radar
  probe.py       (71)      scratch prober, rewritten each round
tests/
  test_brief.py (710)      offline, no network, gates every brief
data/watchlist.txt         dated events Kabil maintains by hand
state/latest.json          yesterday's figures, committed by the run itself
trigger/apps-script.gs     the on-time trigger — NOT YET INSTALLED
docs/trigger-setup.md      its walkthrough, checkpoint by checkpoint
README.md                  setup, source table, design rationale
PROJECT_STATE.md           this file
```

---

## §7 · THE BRIEF IN BRIEF

Nine sections, in order, all Lisbon-time:

| Section | Content | Source |
|---|---|---|
| THE SETUP | Three lines: BTC with day-over-day delta and range position, top USD risk today, latest ETF flow | derived |
| CALENDAR | Today's High/Medium events with actual/forecast; forward view to end of week | ForexFactory JSON |
| **AHEAD** | Countdown to every dated policy/geopolitical event, repeated daily until it passes | Federal Register + watchlist |
| **POLICY DESK** | Warsh remarks and FOMC releases; buyback sizes; coupon auction calendar | Fed RSS + Fiscal Data + TreasuryDirect |
| CRYPTO | BTC/ETH/SOL with deltas, ranges, VWAP; options max pain and OI | Kraken + Deribit |
| FLOWS | BTC ETF net flow, per-fund, 6-day run with sign-flip flag | TFTC (CC BY 4.0) |
| DERIVATIVES | Perp funding and OI, flagged when elevated or negative | Deribit, single venue, labelled |
| SENTIMENT | Fear & Greed with day and week deltas; total mcap and dominance | alternative.me + CoinGecko |
| MACRO & EQUITIES | DXY, 10Y, gold, WTI, VIX, S&P and Nasdaq futures, each with an age stamp | Yahoo chart API |
| RISK WINDOWS | Only windows still ahead; weekends suppress the cash session; a policy date landing today appears here | derived |

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
3. Nine sources fetched, each wrapped so a failure degrades one line
4. Brief rendered, emailed, state committed
5. Scheduled cron fires late  ->  sees last_sent_date  ->  exits silently
6. Kabil reads the "built HH:MM LIS" line and logs delivered-vs-target
7. Weekly: confirm watchlist entries, add events he hears about
8. New source proposed  ->  PROBE FIRST  ->  §12.2 entry  ->  only then wire
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
| Fiscal Data buybacks | `S0` `S8` | 🟢 LIVE | results only — no future-dated operations exist in the set |
| TreasuryDirect upcoming | `S0` | 🟢 LIVE | coupon auction calendar |
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
| Fed-path odds (any free source) | `S2` `S6` | ⚫ EXCLUDED | needs contract-level Fed Funds settlements |
| ETH ETF flows | — | ❓ | TFTC is Bitcoin-only; no free replacement found |

### §12.3 Promotion ladder

| 🔴 DOCUMENTED | 🟡 PROBED | 🟠 WIRED | 🟢 LIVE |
|---|---|---|---|
| Someone says it works. Counts for nothing | 200 from an Actions runner **and** its payload shape read | Fetcher written, degradation path tested, offline tests pass | Correct output observed in a real brief, with the run id recorded |

⚫ **EXCLUDED** — probed and failed, or paid. **Stop re-attempting it.** An
excluded entry is worth as much as a live one: it is what stops the same dead
API being rediscovered enthusiastically in six months.

### §12.4 Kill criterion

A 🟢 LIVE source that renders `unavailable` in **three consecutive briefs** is
demoted to 🟡 and re-probed before anything is rewritten against it. Farside sat
at `unavailable` for twelve days before anyone checked why; that is the
behaviour this criterion exists to prevent.

### §12.5 The uncomfortable consequence

The bar in §12.3 means a new section costs three to nine probe rounds before a
line of fetcher is written, and each round is a commit, a dispatch and a log
read. That is slow, and it is the reason the sections that exist are correct.
It is also why the comfortable-work trap in §8 bites so hard: this process is
genuinely satisfying and it is not the bottleneck. **The bottleneck is a Google
consent screen.**

### §12.6 Toward a complete system

```
1. Trigger installed              -> brief arrives on time          [BLOCKED ON KABIL]
2. One week of delivered-vs-target -> timing declared solved or not
3. Watchlist populated with the events he actually trades
4. Only then: new sources, and only through §12.3
```

*A longer brief is an output of a brief that arrives, not a substitute for one.*

---

**Standing instruction.** At the end of every session on this project: update
§1 if the phase changed, §2 with any new measurement, §4 with decisions and
retractions, §5 with what opened or closed, §10 with the session, §12.2 with
every source tried including the dead ones — then write the §11 entry, increment
the revision, and update the header date.
