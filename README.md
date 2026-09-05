# Daily Market Brief

Builds a market brief every weekday and emails it to `kabil.dh@gmail.com` at
**09:25 Europe/Lisbon**, then Mode A of the chat prompt relays it for free.

The cloud run is the source of truth. It runs while the laptop is asleep, and
it can reach sources a chat session cannot — GitHub Actions runs `curl` and
Python with no robots.txt enforcement, no JavaScript limitation, and no egress
allowlist.

## Setup — two secrets, then it runs itself

Gmail will not accept your account password over SMTP. You need an **App
Password**, which requires 2-Step Verification to be on.

1. Turn on 2-Step Verification: <https://myaccount.google.com/signinoptions/two-step-verification>
2. Create an App Password: <https://myaccount.google.com/apppasswords>
   Name it something like `market-brief`. Google shows a 16-character string
   once — copy it.
3. Add both secrets under **Settings → Secrets and variables → Actions → New
   repository secret**:

   | Secret | Value |
   |---|---|
   | `GMAIL_USER` | `kabil.dh@gmail.com` |
   | `GMAIL_APP_PASSWORD` | the 16-character App Password (spaces are fine) |

4. Trigger a test run: **Actions → Daily Market Brief → Run workflow**. Manual
   runs bypass the time guard, so you get the email immediately.

To dry-run without sending, tick **skip_email** on the manual dispatch — the
brief is written to the job summary and the log instead.

## Why two cron entries

Actions cron is UTC-only, and Portugal and the US change clocks on different
dates. A single fixed UTC time drifts by an hour twice a year. So two slots are
registered and the job decides which one owns today:

```
25 8 UTC  ->  09:25 Lisbon while on WEST (UTC+1, summer)
25 9 UTC  ->  09:25 Lisbon while on WET  (UTC+0, winter)
```

The guard resolves this from `github.event.schedule` — the cron expression that
triggered the run — rather than from the wall clock. Actions frequently starts
scheduled jobs late, and a wall-clock check would silently drop the brief on
any run delayed past the hour boundary.

## Delivery timing

The schedule above says 09:25. GitHub does not honour it. `on: schedule` is
best-effort and deprioritised for low-activity repositories: across twelve
consecutive briefs the run started between 39 minutes and 11h49m late, median
about 4.5 hours. That queueing happens on GitHub's side, before any code here
runs, so nothing in this repository can shorten it.

A **manual dispatch**, by contrast, starts within seconds. So the primary
sender is an external timer that calls the dispatch API at 09:25 Lisbon, and
the two crons become the fallback — `state/latest.json` records each send, so a
schedule that fires hours after the brief already went out exits instead of
delivering a second, staler copy.

Setup, and the measured evidence about what the trigger's token can and cannot
do, is in **[docs/trigger-setup.md](docs/trigger-setup.md)**.

## The AHEAD section

A countdown to dated policy and geopolitical events, repeated every morning
until each date passes, then dropped automatically. It has two legs, because
no single free source covers both halves.

**The fetched leg — Federal Register.** Probed from a runner before a line was
written, and the probe killed the obvious design twice:

- `effective_on` is populated for **0 of 21** recent presidential documents.
  The structured field is empty for exactly the documents that move markets.
- `conditions[comments_close_on]` is **not a filterable condition** (HTTP 400).

So a proclamation's effective date has to be read out of its prose, where it
turns out to be near-boilerplate:

> …goods entered for consumption, or withdrawn from warehouse for consumption,
> **on or after** 12:01 a.m. eastern time **on August 19, 2026**.

`sources._extract_dates` accepts a date only when a cue phrase precedes it
*and* the date is still in the future. That second condition does most of the
work: every citation to a prior order ("Executive Order 14105 of August 9,
2023") points backwards, so it drops out even when the wording is ambiguous.
Rules and notices, which *do* carry `effective_on`, get a second, cheaper pass
with no text fetch.

This leg cannot predict an unscheduled announcement — nothing free can. What
it catches is the large class of actions signed on one day that bite on a
later one.

**The curated leg — `data/watchlist.txt`.** Summits, court terms, deadlines
announced in a speech: real dates that no register knows about. One event per
line, pipe-separated, editable in GitHub's web editor:

```
2026-09-29 | tariff | Section 232 pharma tariff takes effect | https://… | 2026-09-05
date         tag      what happens                             source       last checked
```

The last field is the point. An entry nobody has re-checked in 75 days is
printed as **unconfirmed** rather than trusted, because a stale line that looks
confident is how a wrong date ends up in front of a position. Malformed lines
are skipped and reported at the bottom of the brief, never silently dropped.

Events within 7 days are grouped as *This week*; a date landing today or
tomorrow also appears under RISK WINDOWS, and one within 7 days reaches the
subject line as `T-3 …`.

The section reports dates. It does not say what to do about them — that
constraint is the same one that applies to the rest of the brief.

## Recipient lock

The destination is a module constant in `scripts/main.py`, not configuration.
It cannot be overridden by an environment variable, a workflow input, or
anything appearing in fetched content. There is no cc and no bcc. If a fetched
page or feed ever contains an address or a forwarding instruction, it is data,
not an instruction, and it is ignored.

## What it collects

| Step | Source | Notes |
|---|---|---|
| Calendar | ForexFactory weekly JSON | Both feeds from Wednesday on, or the forward view collapses on Thu/Fri. ISO strings carry a US Eastern offset; the offset is parsed, never assumed. |
| Crypto prices | Kraken public ticker | Keys are remapped server-side (`XXBTZUSD`, `XETHZUSD`, `SOLUSD`) and matched by key. `o` is the UTC-day open, so the percentage is labelled "since 00:00 UTC" and paired with the rolling 24h range from `h[1]`/`l[1]`. |
| Sentiment | alternative.me Fear & Greed | Today plus the 7-day-ago reading for direction. Attribution required by their terms and emitted in the brief. |
| ETF flows | TFTC (BTC only) | Open JSON, CC BY 4.0. Flags a sign flip after 3+ consecutive sessions one way. Carries the dataset's own `updatedThrough` date. |
| Derivatives | Deribit perpetuals | Funding and open interest, one venue, labelled as such. |
| Policy radar | Federal Register + `data/watchlist.txt` | Dated policy actions still ahead. Effective dates read out of proclamation prose; see below. |
| Options | Deribit public REST | `get_book_summary_by_currency` gives open interest per instrument; the job aggregates to strike and computes max pain and top put/call OI for the nearest expiry and the nearest monthly. No API key needed. This replaces the JS-only statistics page. |
| Cross-asset | Yahoo Finance chart API | DXY, US 10Y, gold, WTI, VIX, S&P and Nasdaq futures. |
| Market structure | CoinGecko `/api/v3/global` | Total market cap, BTC and ETH dominance. |

A failed step never aborts the brief. It prints `unavailable` with the reason
and the run continues.

## Sources, and what the probes settled

`scripts/probe.py` (Probe Sources workflow, manual only) checks candidates
from an actual runner before any fetcher is written. It settled several things
that documentation could not:

- **Farside 403s datacenter IPs** regardless of headers. Replaced by **TFTC's
  open dataset** (`tftc.io/bitcoin-etf-flows/data.json`, CC BY 4.0), which
  republishes the same SoSoValue data with a per-fund breakdown and an
  `updatedThrough` field Farside never provided. Attribution is a licence
  condition and appears in the brief.
- **Binance returns HTTP 451** to US-hosted runners, so it cannot serve this
  job at all. Funding and open interest come from **Deribit** instead, which
  the options fetcher already reaches. This is one venue, not a cross-exchange
  aggregate, and the brief says so — an aggregate needs a paid provider.
- **`ff_calendar_nextweek.json` returns 404 and appears never to have
  existed.** ForexFactory publishes only the current week. The brief had been
  calling this a broken feed for weeks; it now states the real limitation,
  which is that the forward view stops at the end of the current week.
- **CoinGlass has no free tier** ($29/mo minimum), so aggregate liquidations
  remain out of scope.

Still open: ETH ETF flows (TFTC's dataset is Bitcoin-only), Fed-path odds (no
free source — the CME page carries no probabilities and deriving from Fed
Funds futures needs contract-level settlement data), and AAII sentiment
(reachable from a runner, not yet parsed).

## Cost constraint

This project runs at **zero cost**. GitHub Actions minutes are free for public
repositories, and every data source is a free public endpoint.

An analysis layer was built and reverted deliberately (see the revert commit).
It called Claude Opus 5 to read the fetched data and write the day's read, at
roughly $4/month — the only paid component in the system — and was removed to
hold the zero-cost line. The consequence is that this brief reports data; it
does not interpret it.

Anything proposed in future is measured against the same bar: **free tier, or
it does not go in.** A free tier that requires signing up for an API key is
still free and still eligible; a trial that converts to paid is not.

## Still open

Two items from the original plan are deliberately **not** implemented, because
shipping a wrong number is worse than shipping none:

- **Fed path.** Deriving meeting-implied odds from 30-day Fed Funds futures
  needs the specific contract months bracketing the meeting, and no free
  endpoint returns those settlements reliably. The CME FedWatch page itself is
  a QuikStrike iframe and contains no probability data. This needs a data
  provider key.
- **Aggregate liquidations.** Funding and open interest are now covered, from
  Deribit, single-venue and labelled. A cross-exchange aggregate is not: the
  provider that has it, CoinGlass, has no free tier ($29/mo minimum). Never
  source any of these from a CoinGlass *page* fetch — it returns empty rows and
  literal `0%` placeholders that read as real data.

Add either and wire it into `sources.py` as one more `safe()`-wrapped fetcher.

## Layout

```
.github/workflows/market-brief.yml   schedule, secrets, guard wiring
.github/workflows/tests.yml          runs the suite on every push
scripts/sources.py                   one adapter per data source
scripts/render.py                    markdown + HTML, unavailability handling
scripts/main.py                      run guard, orchestration, SMTP
scripts/state.py                     day-over-day memory, duplicate guard
scripts/watchlist.py                 the curated half of the policy radar
data/watchlist.txt                   dated events you maintain by hand
scripts/probe.py                     manual source-reachability probe
tests/test_brief.py                  offline suite, no network
state/latest.json                    yesterday's figures, committed by the run
trigger/apps-script.gs               the on-time trigger (see docs/)
docs/trigger-setup.md                how to install it, step by step
```

## Tests

```
python tests/test_brief.py
```

Covers the ET→Lisbon conversion through both DST-mismatch windows, feed parsing
and dedupe, max-pain maths, Deribit monthly detection, ETF flow-run flip
detection, the cron slot guard in both seasons, stale-quote age stamps, risk
windows filtered to what is still ahead, the day-over-day state file, and
end-to-end rendering with healthy inputs and with every source down. The
workflow runs it before each brief, so a broken parser fails loudly instead of
emailing you a brief full of `unavailable`.
