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
   | `ANTHROPIC_API_KEY` | an API key from console.anthropic.com — powers the analysis section |

4. Trigger a test run: **Actions → Daily Market Brief → Run workflow**. Manual
   runs bypass the time guard, so you get the email immediately.

To dry-run without sending, tick **skip_email** on the manual dispatch — the
brief is written to the job summary and the log instead.

## The analysis section

`scripts/analyst.py` passes everything the fetchers returned to Claude Opus 5,
which reads it and writes the day's read, the tensions in the data, and what to
watch. Roughly **$0.18 a run, ~$4/month** at one weekday run.

Three properties keep it honest:

- **The fetchers stay the source of truth.** The model reads their figures; it
  never re-derives them. Anything it retrieves itself must carry a source and a
  date inline, or be omitted — an undated number in this domain is worse than a
  missing one.
- **Retrieval is allowlisted.** `ALLOWED_DOMAINS` in `analyst.py` is the whole
  reachable surface. The quarantined sources are absent from it, so the
  quarantine is structural rather than a request the model could ignore.
- **It cannot cost you the brief.** The call is wrapped in the same `safe()`
  guard as every fetcher. If it fails, the email still goes out with the data
  alone and says the analysis is unavailable.

`web_search` and `web_fetch` here run on Anthropic's infrastructure, not on the
Actions runner — which is why the analyst may reach sources the runner cannot.
See the Farside note below.

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
| ETF flows | Farside BTC + ETH | Parentheses are negative. Flags a sign flip after 3+ consecutive sessions one way. |
| Options | Deribit public REST | `get_book_summary_by_currency` gives open interest per instrument; the job aggregates to strike and computes max pain and top put/call OI for the nearest expiry and the nearest monthly. No API key needed. This replaces the JS-only statistics page. |
| Cross-asset | Yahoo Finance chart API | DXY, US 10Y, gold, WTI, VIX, S&P and Nasdaq futures. |
| Market structure | CoinGecko `/api/v3/global` | Total market cap, BTC and ETH dominance. |

A failed step never aborts the brief. It prints `unavailable` with the reason
and the run continues.

## Known upstream limits

Established by live runs, not assumed:

- **`ff_calendar_nextweek.json` returns HTTP 404.** The this-week feed is
  healthy (99 events on the run that established this), but the next-week URL
  is dead upstream. The consequence is that on Thursday and Friday the
  "next 5 sessions" view loses next week's events. The brief says so
  explicitly rather than printing "none scheduled", which would read as an
  all-clear. If you find the correct URL, it is one constant in
  `sources.py`.
- **Farside returns HTTP 403 to GitHub Actions runners.** Tried with a plain
  agent, a browser user agent, and a full set of `Sec-Fetch` navigation
  headers; all three refused, which makes this IP-level blocking of
  datacenter ranges rather than a header problem. Both ETF flow sections
  therefore report unavailable on the cloud run. The fetcher is left in
  place because it works from a residential IP.

  `farside.co.uk` is on the analyst's allowlist for exactly this reason: its
  `web_fetch` originates from Anthropic's infrastructure, not the runner, so
  it is not subject to that block. Whether it actually retrieves the table is
  the open question — check the analysis section of a run for a dated flows
  figure before assuming the gap is closed.

## Still open

Two items from the original plan are deliberately **not** implemented, because
shipping a wrong number is worse than shipping none:

- **Fed path.** Deriving meeting-implied odds from 30-day Fed Funds futures
  needs the specific contract months bracketing the meeting, and no free
  endpoint returns those settlements reliably. The CME FedWatch page itself is
  a QuikStrike iframe and contains no probability data. This needs a data
  provider key.
- **Aggregate liquidations / funding / OI.** Coinglass's free tier covers all
  three, but it needs an API key. Never source these from a Coinglass *page*
  fetch — it returns empty rows and literal `0%` placeholders that read as
  real data.

Add either and wire it into `sources.py` as one more `safe()`-wrapped fetcher.

## Layout

```
.github/workflows/market-brief.yml   schedule, secrets, guard wiring
.github/workflows/tests.yml          runs the suite on every push
scripts/sources.py                   one adapter per data source
scripts/render.py                    markdown + HTML, unavailability handling
scripts/main.py                      run guard, orchestration, SMTP
tests/test_brief.py                  offline suite, no network
```

## Tests

```
python tests/test_brief.py
```

Covers the ET→Lisbon conversion through both DST-mismatch windows, feed parsing
and dedupe, max-pain maths, Deribit monthly detection, Farside negative
parsing, ETF flow-run flip detection, the cron slot guard in both seasons, and
end-to-end rendering with healthy inputs and with every source down. The
workflow runs it before each brief, so a broken parser fails loudly instead of
emailing you a brief full of `unavailable`.
