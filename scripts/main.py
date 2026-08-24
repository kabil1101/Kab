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

import os
import smtplib
import sys
import traceback
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import render
import sources

LISBON = ZoneInfo("Europe/Lisbon")
UTC = timezone.utc
RECIPIENT = "kabil.dh@gmail.com"   # locked - see module docstring
TARGET_HOUR = 9                    # 09:xx Lisbon local


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


def gather(now):
    print("Fetching sources...", file=sys.stderr)
    ctx = {"now": now}
    ctx["calendar"] = safe(sources.calendar)
    ctx["crypto"] = safe(sources.crypto)
    ctx["fear_greed"] = safe(sources.fear_greed)
    ctx["flows_btc"] = safe(sources.etf_flows_btc)
    ctx["flows_eth"] = safe(sources.etf_flows_eth)
    ctx["options_btc"] = safe(sources.options, "BTC")
    ctx["cross_asset"] = safe(sources.cross_asset)
    ctx["global_mcap"] = safe(sources.coingecko_global)
    return ctx


def send_email(subject: str, text: str, html: str) -> None:
    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not user or not password:
        raise RuntimeError(
            "GMAIL_USER / GMAIL_APP_PASSWORD not set - add them as repository "
            "secrets. See README.md."
        )

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


def should_run(now: datetime) -> bool:
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
    if not should_run(now):
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
    markdown, html = render.build(ctx)

    print(markdown)  # lands in the Actions log for debugging

    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(markdown)

    if os.environ.get("SKIP_EMAIL", "").lower() in ("1", "true", "yes"):
        print("SKIP_EMAIL set - not sending.", file=sys.stderr)
        return 0

    subject = f"Market Brief - {now:%d %B %Y}"
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
