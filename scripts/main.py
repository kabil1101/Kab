#!/usr/bin/env python3
"""Daily market brief: fetch, render, email.

Run guard
---------
GitHub Actions cron is UTC-only, so the workflow fires at two UTC times and
exactly one of them is 09:xx in Lisbon: the earlier one in summer (WEST,
UTC+1), the later one in winter (WET, UTC+0). The guard resolves which slot
this run belongs to from `github.event.schedule` - the cron expression that
triggered it - rather than from the current clock. That distinction matters:
Actions routinely starts a scheduled job late, and a wall-clock check would
silently drop the brief on any run delayed past the hour boundary.

Recipient lock
--------------
The destination address is a module constant, not configuration. It cannot be
overridden by an environment variable, a workflow input, or anything appearing
in fetched content. There is no cc and no bcc.
"""

from __future__ import annotations

import json
import os
import smtplib
import sys
import traceback
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import health
import render
import sources
import state
import watchlist

LISBON = ZoneInfo("Europe/Lisbon")
UTC = timezone.utc
RECIPIENT = "kabil.dh@gmail.com"   # locked - see module docstring
# One definition of "on time", shared with the latency check, so the slot
# guard below and the banner in the brief can never disagree about it.
TARGET_HOUR = health.TARGET_HOUR   # 09:xx Lisbon local

# The PM edition anchors to NEW YORK, not Lisbon (D18). The Lisbon-NY gap is
# 4, 5 or 6 hours depending on the week, so two Lisbon cron slots are
# registered and the job checks which one lands on the target New York hour -
# the same D5 pattern the morning brief already uses, and for the same reason.
# One definition, in health.py, so the dispatch guard here and the latency
# check there can never disagree about when the PM edition was due.
PM_TARGET_HOUR_NY = health.PM_TARGET_HOUR_NY   # 08:xx New York
NEW_YORK = ZoneInfo("America/New_York")

# The two UTC cron slots registered for the PM edition, as (minute, hour).
# Declared rather than derived from the New York hour: which of them lands on
# 08:00 New York changes with US daylight saving, and both must resolve to the
# PM edition so that should_run_pm is the thing that rejects the non-owner -
# with its own message - rather than the morning guard rejecting it with a
# misleading one.
PM_CRON_SLOTS = ((0, 12), (0, 13))
SHADOW_PATH = (state.STATE_PATH.parent / "shadow.jsonl")


def _slot(schedule) -> tuple[int, int] | None:
    """(minute, hour) from a cron expression, or None if it is not one."""
    parts = (schedule or "").strip().split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def edition(env=None, schedule=None) -> str:
    """`am` (the default, and every existing caller) or `pm`.

    An explicit `BRIEF_EDITION` wins - that is the Apps Script dispatch and a
    manual run. Otherwise it is resolved from the cron that fired.

    **This used to live in the workflow YAML and silently produced an empty
    string**, so both PM cron slots ran the MORNING path, hit the morning's
    duplicate guard and exited without a word about the PM edition. The
    fallback behind the whole afternoon edition was dead on arrival and the
    run still reported success.

    It lives here now for one reason: this can be tested and a `${{ }}`
    expression cannot. The test that was supposed to cover it asserted the
    YAML *contained* the expression, which stayed green while the expression
    did nothing - a test on a config line's presence rather than its
    behaviour.
    """
    env = (env if env is not None
           else os.environ.get("BRIEF_EDITION") or "").strip().lower()
    if env in ("am", "pm"):
        return env
    if schedule is None:
        schedule = os.environ.get("BRIEF_SCHEDULE")
    return "pm" if _slot(schedule) in PM_CRON_SLOTS else "am"


def should_run_pm(now: datetime, prev: dict | None = None) -> bool:
    """Whether this run is the PM slot that owns today.

    Its own duplicate marker, never the morning's: by the time the PM runs,
    `last_sent_date` is today for the ordinary reason that the morning brief
    went out, and sharing the guard would suppress the PM edition every day.
    """
    # Same escape hatch the morning guard has had since the start. Without
    # it the PM edition cannot be dry-run on a runner once the real one has
    # gone out - which is exactly when a change most needs proving, and it
    # blocked a verification run on 20 Sep.
    if os.environ.get("FORCE_RUN", "").lower() in ("1", "true", "yes"):
        return True

    schedule = (os.environ.get("BRIEF_SCHEDULE") or "").strip()
    if prev and state.already_sent_pm_today(prev, now.date()):
        print(f"A PM edition for {now:%Y-%m-%d} was already sent. Exiting.",
              file=sys.stderr)
        return False
    if not schedule:
        return True
    parts = schedule.split()
    try:
        minute, hour = int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        print(f"Unparseable schedule {schedule!r}; proceeding.", file=sys.stderr)
        return True
    slot_ny = now.astimezone(UTC).replace(
        hour=hour, minute=minute, second=0, microsecond=0).astimezone(NEW_YORK)
    if slot_ny.hour != PM_TARGET_HOUR_NY:
        print(f"Schedule {schedule!r} maps to {slot_ny:%H:%M} New York "
              f"({slot_ny.tzname()}); the other slot owns today. Exiting.",
              file=sys.stderr)
        return False
    print(f"Schedule {schedule!r} -> {slot_ny:%H:%M} New York. Proceeding.",
          file=sys.stderr)
    return True


def write_shadow(now, shadow: dict, body_count: int) -> None:
    """D20: record what the body WOULD have said, whether or not it said it.

    Ships in the same commit as the edition on purpose. Retrofitting it throws
    away the only evidence that can replace v1's fixed thresholds with
    range-scaled ones, and about two weeks of it is what that needs.
    """
    if not shadow:
        return
    row = {"at": now.isoformat(), "printed": body_count, "moves": shadow,
           "thresholds": render.THRESHOLDS}
    try:
        SHADOW_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SHADOW_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError as exc:
        print(f"::warning::could not append the shadow log "
              f"({type(exc).__name__}); thresholds stay on v1 longer",
              file=sys.stderr)


def safe(fn, *args, **kwargs):
    """Run a fetcher. A failed step never aborts the brief."""
    try:
        return {"ok": True, "data": fn(*args, **kwargs), "error": None}
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()          # full detail stays in the run log
        msg = " ".join(str(exc).split()) or type(exc).__name__
        if len(msg) > 160:             # backstop: never let a fetcher's error
            msg = msg[:159] + "\u2026"  # text swamp the rendered brief
        print(f"  [degraded] {fn.__name__}: {msg}", file=sys.stderr)
        return {"ok": False, "data": None, "error": msg}


class LazyContext(dict):
    """A ctx that fetches a source the first time something reads it.

    §3.36. `gather` used to fetch all 21 sources before either edition
    rendered a line. The PM edition renders about half of them, so it sat
    waiting on FRED - which it never prints - through FRED's own scheduled
    maintenance. Measured on three identical runs: 13s outside the window,
    43s as it opened, 100s inside it.

    **Why lazy rather than a per-edition list of what to skip.** A skip list
    is a claim about what the renderer reads, and §12.4a is the section about
    claims decaying. Two attempts to derive that list were both wrong, in two
    different ways:

      - an AST trace missed `perp_eth`, because it is reached through a loop
        variable rather than a literal key;
      - a runtime recorder missed `plumbing`, because the read sits inside
        `if backdrop is not None` and the fixture had no backdrop. A
        measurement only sees the branches its data reaches.

    Either error ships a section that is silently empty, which is the failure
    this file already has three sections about. **Lazy needs no list**: what
    is read is fetched, what is not read is not, and a line added tomorrow
    fetches its own source without anyone remembering to update anything.

    Iteration forces everything, because `build` ends by listing the sources
    that failed and a half-resolved ctx would under-report that. The morning
    edition therefore still fetches all 21; the PM edition never iterates.
    """

    def __init__(self, base=None, fetchers=None):
        super().__init__(base or {})
        self._pending = dict(fetchers or {})

    def _resolve(self, key):
        fn = self._pending.pop(key, None)
        if fn is None:
            return
        print(f"  fetching {key}", file=sys.stderr)
        dict.__setitem__(self, key, fn())

    def _resolve_all(self):
        for key in list(self._pending):
            self._resolve(key)

    # --- reads ----------------------------------------------------------
    def __getitem__(self, key):
        self._resolve(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        # dict.get is implemented in C and never calls __getitem__, so it has
        # to be overridden explicitly or every ctx.get() would miss its fetch.
        self._resolve(key)
        return super().get(key, default)

    def __contains__(self, key):
        return key in self._pending or super().__contains__(key)

    # --- writes ---------------------------------------------------------
    def __setitem__(self, key, value):
        self._pending.pop(key, None)   # an explicit value beats a fetcher
        super().__setitem__(key, value)

    # --- anything that walks the whole thing ----------------------------
    def keys(self):
        self._resolve_all()
        return super().keys()

    def values(self):
        self._resolve_all()
        return super().values()

    def items(self):
        self._resolve_all()
        return super().items()

    def __iter__(self):
        self._resolve_all()
        return super().__iter__()

    def __len__(self):
        self._resolve_all()
        return super().__len__()


def _watchlist():
    """Not wrapped in safe(): the watchlist reads a local file and already
    degrades to an empty list, so the only thing left to guard against is a
    bug in the parser itself."""
    try:
        return watchlist.load()
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        return {"events": [],
                "problems": [f"unreadable ({type(exc).__name__})"]}


def gather(now):
    print("Fetching sources...", file=sys.stderr)
    today = now.date()
    return LazyContext({"now": now}, {
        "calendar": lambda: safe(sources.calendar),
        "crypto": lambda: safe(sources.crypto),
        "fear_greed": lambda: safe(sources.fear_greed),
        "flows_btc": lambda: safe(sources.etf_flows_btc),
        "perp_btc": lambda: safe(sources.perp_stats, "BTC"),
        "perp_eth": lambda: safe(sources.perp_stats, "ETH"),
        "options_btc": lambda: safe(sources.options, "BTC"),
        "cross_asset": lambda: safe(sources.cross_asset),
        "global_mcap": lambda: safe(sources.coingecko_global),
        "policy_radar": lambda: safe(sources.policy_radar, today),
        "fed_officials": lambda: safe(sources.fed_officials, today),
        "treasury_ops": lambda: safe(sources.treasury_ops, today),
        "policy_rate": lambda: safe(sources.policy_rate),
        "fed_odds": lambda: safe(sources.fed_odds, today),
        "inflation": lambda: safe(sources.inflation),
        # Commit 3. Both degrade to a named `unavailable` like everything
        # else: backdrop needs FRED_API_KEY and FRED has a scheduled outage
        # in the watchlist; news is two independent feeds and either can go
        # quiet.
        "backdrop": lambda: safe(sources.backdrop, today),
        "news": lambda: safe(sources.news, now),
        # Rounds 18 and 19. Liquidations close the largest gap between
        # Kabil's framework and this brief; the Yahoo extras and the plumbing
        # come from the addendum, now closed.
        "liquidations": lambda: safe(sources.liquidations),
        "yahoo_extra": lambda: safe(sources.yahoo_extra),
        "plumbing": lambda: safe(sources.plumbing, today),
        "watchlist": _watchlist,
    })


def credentials() -> tuple[str, str]:
    """The SMTP login, or a RuntimeError naming exactly what is missing.

    Split out of `send_email` so it can be tested without opening a socket.
    It was not, and the test that covered it made a real connection to Gmail
    and a real failed login attempt on every run - in a suite whose own
    docstring promises no network. That is slow wherever SMTP is blocked, and
    a repeated failed auth from a shared CI address is a good way to get an
    account throttled.
    """
    user = (os.environ.get("GMAIL_USER") or "").strip()
    # Google displays App Passwords in four space-separated groups
    # ("abcd efgh ijkl mnop"). People paste them exactly as shown, so strip
    # whitespace rather than failing authentication on a cosmetic detail.
    password = "".join((os.environ.get("GMAIL_APP_PASSWORD") or "").split())
    missing = [n for n, v in (("GMAIL_USER", user),
                              ("GMAIL_APP_PASSWORD", password)) if not v]
    if missing:
        # Name each one separately. "both missing" and "one missing" are
        # different mistakes and need different fixes, and an empty value here
        # means the repository secret does not exist under that exact name -
        # Actions substitutes an empty string for a secret it cannot find.
        raise RuntimeError(
            f"missing repository secret(s): {', '.join(missing)}. "
            f"Add them at Settings -> Secrets and variables -> Actions with "
            f"exactly these names. See README.md."
        )
    return user, password


def send_email(subject: str, text: str, html: str) -> None:
    user, password = credentials()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=60) as s:
        s.login(user, password)
        s.sendmail(user, [RECIPIENT], msg.as_string())
    print(f"Sent to {RECIPIENT}", file=sys.stderr)


def should_run(now: datetime, prev: dict | None = None) -> bool:
    """Decide whether this invocation is the one that maps to 09:xx Lisbon.

    Resolved from the triggering cron expression, not the wall clock, so a
    late start does not drop the brief.
    """
    if os.environ.get("FORCE_RUN", "").lower() in ("1", "true", "yes"):
        return True

    schedule = (os.environ.get("BRIEF_SCHEDULE") or "").strip()
    if not schedule:
        # Manual dispatch or local run: always proceed.
        return True

    # From here down this is a *scheduled* run, which is only the fallback
    # behind an external trigger. GitHub fires these hours late, so if the
    # brief already went out today, sending again would deliver a second copy
    # with staler numbers than the one already read.
    if prev and state.already_sent_today(prev, now.date()):
        print(f"A brief for {now:%Y-%m-%d} was already sent; this scheduled "
              f"run is a duplicate. Exiting.", file=sys.stderr)
        return False

    parts = schedule.split()
    if len(parts) < 2:
        print(f"Unparseable schedule {schedule!r}; proceeding.", file=sys.stderr)
        return True
    try:
        minute, hour = int(parts[0]), int(parts[1])
    except ValueError:
        print(f"Unparseable schedule {schedule!r}; proceeding.", file=sys.stderr)
        return True

    slot_utc = now.astimezone(UTC).replace(
        hour=hour, minute=minute, second=0, microsecond=0)
    slot_lis = slot_utc.astimezone(LISBON)
    if slot_lis.hour != TARGET_HOUR:
        print(
            f"Schedule {schedule!r} maps to {slot_lis:%H:%M} Lisbon "
            f"({slot_lis.tzname()}); the other slot owns today. Exiting.",
            file=sys.stderr,
        )
        return False
    print(f"Schedule {schedule!r} -> {slot_lis:%H:%M} Lisbon. Proceeding.",
          file=sys.stderr)
    return True


def main() -> int:
    now = datetime.now(LISBON)
    prev = state.load()
    mode = edition()
    if mode == "pm":
        if not should_run_pm(now, prev):
            return 0
    elif not should_run(now, prev):
        return 0

    sending = os.environ.get("SKIP_EMAIL", "").lower() not in ("1", "true", "yes")
    have_creds = bool(os.environ.get("GMAIL_USER")
                      and os.environ.get("GMAIL_APP_PASSWORD"))
    if sending and not have_creds:
        # Say this up front. Discovering it only after the brief has been
        # built buries the one line that explains the failure.
        print("::warning::GMAIL_USER / GMAIL_APP_PASSWORD are not set - the "
              "brief will be built but cannot be emailed. See README.md.",
              file=sys.stderr)

    ctx = gather(now)
    ctx["prev"] = prev          # yesterday's figures, for day-over-day deltas
    # Whether the delivery system itself is healthy. Computed here, not in the
    # renderer, because this is the only layer that can see the environment.
    # TRIGGER_VERSION is set only by the Apps Script, BRIEF_SCHEDULE only by
    # the cron fallback. A run carrying neither is a human pressing the
    # button, which is why both are passed through rather than collapsed into
    # one flag: the two failures need different words.
    ctx["health"] = health.notes(prev, now.date(),
                                 os.environ.get("TRIGGER_VERSION"),
                                 os.environ.get("BRIEF_SCHEDULE"),
                                 now=now, edition=mode)
    for note in ctx["health"]:
        # Also surfaces on the Actions run page, so a gap is visible to
        # whoever opens GitHub as well as to whoever opens Gmail.
        print(f"::warning::{note}", file=sys.stderr)
    if mode == "pm":
        markdown, html = render.pm_build(ctx)
        body, shadow = render.pm_body(ctx)
        # D20 records what a REAL edition would have printed. A skip_email
        # test dispatch is not one: it runs at whatever hour the testing
        # happens to be at, so its row measures a different interval from the
        # 09:20-to-13:00 window the thresholds are being calibrated for.
        # Three such rows were already in the file before anyone noticed,
        # which is §3.35's lesson a second time - a wrong banner gets seen,
        # a wrong dataset gets averaged.
        if sending:
            write_shadow(now, shadow, len(body))
    else:
        markdown, html = render.build(ctx)

    print(markdown)  # lands in the Actions log for debugging

    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(markdown)

    if os.environ.get("SKIP_EMAIL", "").lower() in ("1", "true", "yes"):
        print("SKIP_EMAIL set - not sending.", file=sys.stderr)
        return 0

    subject = render.pm_subject(ctx) if mode == "pm" else render.subject(ctx)
    sys.stdout.flush()   # keep the failure below the brief, not buried above it
    try:
        send_email(subject, markdown, html)
    except Exception as exc:  # noqa: BLE001
        traceback.print_exc()
        # A GitHub Actions error annotation surfaces on the run page itself,
        # so the cause is visible without scrolling the log at all.
        print(f"::error::Brief built successfully but could not be emailed: "
              f"{' '.join(str(exc).split())}", file=sys.stderr)
        return 1

    # Only after a confirmed send. `last_sent_date` means sent, not built, or
    # the duplicate guard above would suppress a brief that never arrived.
    try:
        if mode == "pm":
            # The one exception to "the PM writes no state". Everything else
            # in the file belongs to the morning: if the PM overwrote the
            # daily baseline, tomorrow's "vs yesterday" would compare 09:20
            # against this afternoon - a nineteen-hour move labelled as a
            # daily one, which is §3.18 and cost a correction once already.
            state.save(state.pm_mark(prev, now.date()))
            print("PM marker written; the daily baseline is untouched.",
                  file=sys.stderr)
        else:
            state.save(state.snapshot(ctx, sent_on=now.date(), prev=prev))
            print("State written for tomorrow's deltas.", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"::warning::could not write state ({type(exc).__name__}); "
              f"tomorrow's brief will have no deltas", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
