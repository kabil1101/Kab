"""Does the delivery system itself still work?

Every other module here checks the market. This one checks the brief.

It exists because of 12–13 September 2026. The external trigger stopped firing
at weekends, two briefs were never sent, and nothing noticed: not the workflow,
which was never asked to run; not the test suite, which was green; and not
PROJECT_STATE.md, which recorded one of the two missing days as delivered at
09:20. The gap was found only when someone went looking through an inbox.

The reason it was invisible is worth stating plainly, because it generalises:
**the only evidence that a brief exists is the brief, and a brief that was
never sent cannot report its own absence.** So the next one reports it instead.
`state/latest.json` has carried the date of the last confirmed send since
5 September, and until now nothing ever compared that date to today.

Two checks live here.

  - **Delivery gap.** The calendar days between the last confirmed send and
    today. `last_sent_date` is written only after SMTP returns, so it means
    delivered, not attempted — which is exactly what makes it usable as
    evidence.

  - **Trigger drift.** The external trigger's source is in this repository,
    but the copy that actually runs lives in a Google account and is updated
    by hand. The two drift silently, and drifting is what caused the gap
    above. The script now states its version on every dispatch, and a
    disagreement with this module says so in the brief.

Both obey the rule §12.4a cost two wrong verdicts to learn: absence of
evidence is not evidence. No `last_sent_date`, or a dispatch that carries no
version, produces **no claim at all** rather than a guessed one.
"""

from __future__ import annotations

from datetime import date, timedelta

# Bump this whenever trigger/apps-script.gs changes in a way that matters, and
# say so in the setup doc. The installed copy reports its own number on every
# dispatch; a mismatch means someone edited the file here and never re-pasted
# it into Google. That is not hypothetical — it is what happened on 12 Sep.
EXPECTED_TRIGGER_VERSION = "7"

# Past this, name the date instead of listing days. A state file three months
# old is not ninety missed mornings; it is a state file that stopped being
# written, which is a different problem and deserves different words.
MAX_LISTED = 5


def _parse(value) -> date | None:
    """A date from the state file, or None if it is missing or unusable."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def last_sent(prev: dict) -> date | None:
    """The day the last brief was confirmed sent, if the file says."""
    return _parse((prev or {}).get("last_sent_date"))


def baseline_date(prev: dict) -> date | None:
    """The day the comparison figures in the state file were taken."""
    return _parse((prev or {}).get("date"))


def missed_days(prev: dict, today: date) -> list[date]:
    """Calendar days since the last confirmed send that carry no brief.

    Today is excluded — today's brief is the one asking the question. A
    negative or zero gap (a clock skew, a second run the same day, a state
    file from the future) yields nothing, because none of those is a miss.
    """
    last = last_sent(prev)
    if last is None:
        return []
    gap = (today - last).days
    if gap <= 1:
        return []
    return [last + timedelta(days=n) for n in range(1, gap)]


def delivery_note(prev: dict, today: date) -> str | None:
    """One sentence naming the briefs that never arrived, or None."""
    missed = missed_days(prev, today)
    if not missed:
        return None
    last = last_sent(prev)
    noun = "brief" if len(missed) == 1 else "briefs"
    if len(missed) > MAX_LISTED:
        return (f"DELIVERY GAP — {len(missed)} {noun} never sent. Last "
                f"confirmed send {last:%a %d %b}.")
    days = ", ".join(f"{d:%a %d %b}" for d in missed)
    return (f"DELIVERY GAP — {len(missed)} {noun} never sent: {days}. "
            f"Last confirmed send {last:%a %d %b}.")


def trigger_note(reported) -> str | None:
    """One sentence when the installed trigger is not the one in this repo.

    An empty report is a manual dispatch, or a trigger old enough to predate
    version reporting. Neither is evidence of drift, so neither gets a claim.
    """
    reported = str(reported or "").strip()
    if not reported or reported == EXPECTED_TRIGGER_VERSION:
        return None
    return (f"TRIGGER OUT OF DATE — the installed Apps Script reports version "
            f"{reported}; this repository expects {EXPECTED_TRIGGER_VERSION}. "
            f"Re-paste trigger/apps-script.gs (docs/trigger-setup.md).")


def notes(prev: dict, today: date, trigger_version=None) -> list[str]:
    """Every warning the brief should lead with. Empty when all is well."""
    found = (delivery_note(prev, today), trigger_note(trigger_version))
    return [n for n in found if n]
