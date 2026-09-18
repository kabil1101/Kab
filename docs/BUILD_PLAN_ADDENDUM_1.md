# Daily Market Brief — Handoff ADDENDUM 1

2026-09-18 · @Someone

---

> ### ✅ CLOSED AND BUILT — 2026-09-18. Added on commit; not part of it.
>
> **Kabil closed it on 2026-09-18 and all three additions are built.** Its §1
> asked for exactly this signal before anything was built from it, and nothing
> was until it came.
>
> | Addition | Built as |
> |---|---|
> | **A** — OI change against price change | DERIVATIVES, both deltas adjacent, **no label on the pair** (D22) |
> | **B** — liquidity plumbing | BACKDROP: reverse repo, TGA, bank reserves. **No net-liquidity composite**, and the brief says why |
> | **C part 1** — CME weekend note | CYCLE, date math |
> | **C part 2** — the gap measurement | CYCLE, and **probe target 10 passed** — `BTC=F` returns on the same call shape as every other Yahoo symbol |
> | PM threshold | OI ±3%, in the same config block, shadow-logged |
>
> **Its §4 correction was right to make.** Calling the gap "zero cost" would
> have been wrong: the calendar note is date math and the measurement needed a
> price feed nobody had probed. It got probed, and it passed.
>
> **Its §6 was right about the biggest thing.** *"The largest single gap
> between the stated framework and the system"* was liquidations — and probe
> round 18 found OKX answers keyless, overturning a `no free source` verdict
> this project had carried since rev 1. That is now live.
>
> **Its §6 was also honest about its own limits**, which is why the answer it
> gave is recorded and the question stays open: the list came *"from
> inference, not by him from observation."* Two of its three
> proposed-and-not-taken candidates remain untaken — session levels and the
> overnight sweep, and overnight movers.
>
> The body below is unedited. Where it says a thing is unbuilt or unprobed,
> read it as the state on 2026-09-18 before the work, not as the state now.

**This is an addendum to "Daily Market Brief — Handoff to Claude Code", which is already transferred and under build. It adds to that plan; it does not replace or revise it.** Read the original first — every decision, gate and constraint in it still holds.

## 1 · Addendum status

**⚠ This document is OPEN. Do not treat it as a complete spec.** Kabil is still adding to it and will say explicitly when it is final and ready to transfer. Until then, build from the original handoff; this one is a queue, not an instruction set.

**Relationship to the original.** Handoff 1 is transferred and under build. Nothing here revises it. Three additions arrive as new work, and §5 lists exactly which parts of the original plan they extend — the state bundle, BACKDROP, CYCLE, the probe round and the PM threshold block.

**Everything in the original still governs**, unchanged:

- **Gate 0** — nothing new ships until five clean mornings, read from the inbox
- **D2** — zero cost; a free tier behind a free key qualifies, a trial that converts does not
- **D3, D9, D22** — no levels called, no structure named, no interpretation. Number, delta, age stamp
- **D4** — every number fetched that run; `unavailable` is a correct outcome
- **§12.3** — no source is described as working until a runner has answered and its payload shape has been read

**Where these came from.** Kabil asked what I would check every morning that the brief does not carry. Six candidates came back; he selected three. **The other three are recorded in §6 as proposed-and-not-taken, not as rejected** — so nobody rediscovers them and nobody builds them by mistake.

## 2 · Addition A — open interest change against price change

**Section:** DERIVATIVES (Tier 2) · **Source cost:** none — Deribit already fetched · **Other cost:** one field in the state bundle

**The problem: DERIVATIVES prints open interest as a level, and a level says nothing.** OI at 340,000 contracts is meaningless in isolation. **OI *change* read against *price* change is the positioning read** — and the brief currently cannot distinguish the four cases:

| Price | OI | What it mechanically means |
| --- | --- | --- |
| up | up | new money opening longs |
| up | down | existing shorts covering |
| down | up | new money opening shorts |
| down | down | longs closing or being liquidated |

**Price up 1.5% on rising OI and price up 1.5% on falling OI are opposite events wearing the same number.** The brief reports the number and loses the distinction.

### What to build

**Print both deltas adjacent, with no interpretive label:**

```
OI 341,200 contracts · +4.2% 24h  (price +1.1%)
```

**⚠ The label is deliberately omitted, and this is a D3/D22 call.** Writing *"new longs opening"* looks like a mechanical identity, but it is an inference about *who* the marginal participant is — and Kabil rejected level-flagging on exactly this boundary. **With both deltas adjacent the reading is trivial and it stays his.** If he later wants the label, that is a decision to take explicitly, not to drift into.

**Deribit is a single venue** (\~85% of crypto options, but perps are more fragmented). The existing single-venue label extends to this line and must not be dropped.

**State requirement:** prior-run OI. One more field in the 30-day rolling series already specified in the original §7. **It does not need its own schema change** — it rides the bundle.

**PM threshold:** OI ±3% since the 09:20 brief. Into the same config block as the rest; shadow-logged like the rest.

## 3 · Addition B — liquidity plumbing via FRED

**Section:** BACKDROP (Tier 3) · **Source cost:** none — same host, same method, key already a repository secret

**Why it belongs.** BACKDROP as originally specified carries the economic *picture* — unemployment trend, yield curve, CPI trend. These three carry the **mechanism**: the plumbing through which policy actually reaches risk assets. It is the difference between describing the weather and reading the pressure.

| Series | FRED id | Cadence | What it is |
| --- | --- | --- | --- |
| Overnight reverse repo | `RRPONTSYD` | daily | cash parked at the Fed overnight — drained or refilled |
| Treasury General Account | `WTREGEN` | weekly | Treasury's own balance; refilling it pulls cash out of the system |
| Reserve balances | `WRESBAL` | weekly (Wednesday) | what banks actually hold at the Fed |

**Method is already settled** — round 16, unchanged: `output_type=4` with an **explicit** `realtime_start`/`realtime_end`. Never use `releases/dates` to decide publication, and never rely on the default realtime window; both lie.

### Two cautions

**⚠ These series lag, and the brief must say so.** Two are weekly, one is daily with a publication lag. **Every line carries its observation date and its age**, as the rest of the brief already does. A weekly number printed without an age stamp reads as today's — that is the *present-but-misleading* failure, not a missing-data failure.

**⚠ Do not compute a "net liquidity" composite.** The common construct — balance sheet minus TGA minus RRP — is arithmetic with **modelling choices baked into it**, and different desks compute it differently. Printed as a single headline number in the same typeface as fetched data, it would be a derived opinion wearing a fetched number's clothes. That is §3.9 inverted, the thing the brief has never done.

**Print the three components with week-over-week change.** If Kabil later wants the composite, it is an explicit decision with a stated formula — not a default.

**Note already in the watchlist:** FRED carries a scheduled outage. Whatever wires against it degrades to a named `unavailable`, as everything else does.

## 4 · Addition C — the CME weekend gap

**Section:** CYCLE (Tier 1) · **Cost: split — see the correction below**

**⚠ Correction to what I said when I proposed this.** I described the CME weekend gap as *"Monday-morning only, pure date math, zero cost."* **That is half wrong, and the half that is wrong is the useful half.**

- **The calendar note is date math.** When CME closes and reopens is a fixed weekly rule — genuinely zero cost.
- **The gap itself is a measurement.** It needs a CME futures price — Friday's settle against Sunday's open or current spot. **Nothing in the brief currently fetches CME futures.** Whether Yahoo carries the contract on the same call shape as its other tickers is **unverified and unprobed**.

Logging the correction rather than quietly fixing it, per the own-errors-loudly rule.

### What splits out

**Part 1 — build now, zero cost.** A CYCLE line stating CME's weekend session state: closed Friday 17:00 ET, reopens Sunday 18:00 ET, and spot has traded through the gap unhedged. Pure date math, reuses the DST handling already in the plan, and honest on its own.

**Part 2 — needs a probe.** The gap measurement: does it exist, how large, which direction, and has it been filled. **Becomes probe target 10** in the round specified in the original §8:

| # | Target | Question | Pass test | What it changes |
| --- | --- | --- | --- | --- |
| 10 | CME BTC futures via Yahoo | does the contract return on the same call shape as `CL=F` and `BZ=F`, with Friday's settle retrievable? | 200 · settle price · usable timestamp | whether the gap can be measured at all, or only announced |

**If target 10 fails**, Part 1 still ships and the brief says the gap is not measured rather than implying it does not exist. **The calendar note without the measurement is still worth having** — it tells you the weekend was unhedged, which is the risk; the size is the refinement.

**⚠ Do not state whether the gap "should" fill.** The gap's size and direction are fetched facts. *"Gaps tend to fill"* is a claim about future price and falls under D3 and D22.

## 5 · What changes in the original handoff

**Nothing is revised. Five things grow.**

| Original | Was | Becomes |
| --- | --- | --- |
| **State bundle** (§7) | 4 features: PM baseline, days-since counters, volume average, stablecoin 7d | **5** — adds prior-run OI |
| **BACKDROP** (§3) | unemployment trend, yield curve, CPI trend | **+3 series** — RRP, TGA, reserve balances |
| **CYCLE** (§6) | 6 expiry cycles | **7** — adds the CME weekend session note |
| **Probe round** (§8) | 9 targets | **10** — adds CME BTC futures via Yahoo |
| **PM thresholds** (§4) | 10 lines | **11** — adds OI ±3% |

**Build placement, against the original §9:**

- **CME weekend calendar note → Commit 1.** Date math, no new source. It belongs with the rest of CYCLE.
- **OI change → Commit 4**, with the state bundle. It rides an existing schema change.
- **FRED liquidity series → Commit 3**, alongside FRED for BACKDROP. Same host, same method, same wiring pass.
- **Probe target 10 → the existing round.** Still one dispatch, still one log read.
- **OI threshold → the same config block.** Shadow-logged from day one like the rest.

**No new commits. No change to the gate. No change to the dated items** — the token renewal, the DST window, the midterms and the China table refresh all stand as written.

**⚠ One thing to watch.** The state bundle now carries five features and remains the single largest change on the delivery path. The original already flagged it as needing its own testing attention; **a fifth field does not change that judgement, it reinforces it.**

## 6 · Status

**🟡 OPEN — not final, not ready to transfer.** Kabil is still adding. He will say explicitly when this is closed.

### Proposed and not taken — deferred, not rejected

Three of the six candidates were not selected. **They are recorded here so nobody rediscovers them and nobody builds them by mistake.** None was rejected on merit; they were simply not chosen for this round.

| Candidate | Why it was proposed | Why it is not here |
| --- | --- | --- |
| **Liquidations** | Kabil's own framework opens with *"liquidation cascades, not support/resistance magic"*, and **the brief carries no liquidation data at all** — not the level, not the 24h total, not the clusters. The register marks the no-free-source verdict `unconfirmed rather than settled`, and §12.4a is precise about this shape: CoinGlass being paid is a property of that *route*, not of the world. Bitget, Bybit and OKX all run public APIs and none has been probed | Not selected. **This is the largest single gap between the stated framework and the system**, and it remains open |
| **Session levels and the overnight sweep** | Prior-day high/low/close, Asia session high/low, and where price sits against them. Kabil runs a **False Breakout** strategy and the brief carries nothing that serves it. Reporting OHLC is data, so D3 holds | Not selected. It is also the closest any proposal has come to the D3 line — *"the Asia high was traded through and closed back below"* is geometry, *"a False Breakout set up"* is a signal. **If it is ever built, the wording rule is written first, not after** |
| **Overnight movers** | Top gainers and losers across majors. CoinGecko already live, zero cost. Shows where flow went overnight and feeds altcoin screening | Not selected |

### Still open from the original handoff

Unchanged and carried forward:

- ⏳ **The rest of the events Kabil trades around** — four entries exist; the curated leg is still mostly empty. Open since rev 1
- ⏳ **His manual morning checks** — the question that produced this addendum was answered by me from inference, not by him from observation. **His list would be better evidence than mine**
- ⏳ **Whether any Fed speaker beyond Warsh is tracked by name**

### Reminder for whoever builds this

The original's closing line still applies, and applies to this document more than to that one:

> The section count is not the metric. The arrival time is.
