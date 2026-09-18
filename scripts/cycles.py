"""Recurring market structure, derived rather than fetched.

Nothing here makes a request. Every date below follows from a rule — third
Friday, last Friday, thirty days before — so the brief can know about them a
year out and never be wrong because a feed was down.

Two kinds of thing live here.

  - **US market holidays**, needed by the expiry rules (an expiry landing on a
    closed day moves) and by FLOWS, where a closed market means **zero
    creations and redemptions**, which is a true zero and not `unavailable`.
    Getting that distinction wrong makes a real closure read as a broken feed.

  - **Six recurring expiries.** They set the shape of a session — pinning into
    an opex, the roll of open interest after a settlement — and they are
    invisible to every source the brief already reads, because none of them is
    news. They are a calendar.

**The 08:00 UTC problem, stated once.** Deribit settles at 08:00 UTC and the
brief dispatches at 08:20 UTC. On the last Friday of every month the expiring
series has therefore **already settled and rolled off twenty minutes before
the brief builds.** Max pain and open interest jump to the next expiry with no
explanation, and a reader comparing to yesterday sees a discontinuity that
looks like bad data. `rolled_today()` exists so the brief can say so.
"""

from __future__ import annotations

from datetime import date, timedelta

FRIDAY = 4
WEDNESDAY = 2
THURSDAY = 3
QUARTER_MONTHS = (3, 6, 9, 12)


# --------------------------------------------------------------- date rules

def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """The nth given weekday of a month. n=1 is the first."""
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    """The last given weekday of a month."""
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def easter(year: int) -> date:
    """Gregorian Easter Sunday — the anonymous algorithm.

    Here only because Good Friday is the one US market holiday that moves, and
    it is the one that can collide with an expiry.
    """
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


def _observed(day: date) -> date:
    """NYSE observance: Saturday moves back a day, Sunday moves forward."""
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


def us_market_holidays(year: int) -> dict[date, str]:
    """NYSE full closures for a year, by rule.

    Derived, not curated — every one of these is statutory or fixed. Two
    things this cannot know and the watchlist must carry instead: an ad-hoc
    closure (the NYSE shut for a national day of mourning in January 2025) and
    a half-day, which is not a closure at all.
    """
    out = {
        _observed(date(year, 1, 1)): "New Year's Day",
        nth_weekday(year, 1, 0, 3): "Martin Luther King Jr. Day",
        nth_weekday(year, 2, 0, 3): "Washington's Birthday",
        easter(year) - timedelta(days=2): "Good Friday",
        last_weekday(year, 5, 0): "Memorial Day",
        _observed(date(year, 6, 19)): "Juneteenth",
        _observed(date(year, 7, 4)): "Independence Day",
        nth_weekday(year, 9, 0, 1): "Labor Day",
        nth_weekday(year, 11, 3, 4): "Thanksgiving",
        _observed(date(year, 12, 25)): "Christmas Day",
    }
    return out


def is_us_market_holiday(day: date) -> bool:
    return day in us_market_holidays(day.year)


def _shift_back(day: date) -> date:
    """An expiry landing on a closed day moves to the session before it."""
    while is_us_market_holiday(day) or day.weekday() > 4:
        day -= timedelta(days=1)
    return day


# ------------------------------------------------------------- the expiries

def monthly_opex(year: int, month: int) -> date:
    """US equity monthly options expiry — third Friday, Thursday if shut."""
    return _shift_back(nth_weekday(year, month, FRIDAY, 3))


def is_triple_witching(day: date) -> bool:
    """Index futures, index options and single-stock options together.

    Called **triple** witching throughout, never quad: single-stock futures
    were delisted, and two names for one event reads as two events six months
    later.
    """
    return (day.month in QUARTER_MONTHS
            and day == monthly_opex(day.year, day.month))


def vix_expiry(year: int, month: int) -> date:
    """Wednesday 30 days before the FOLLOWING month's third Friday."""
    nxt_y, nxt_m = (year + 1, 1) if month == 12 else (year, month + 1)
    return _shift_back(nth_weekday(nxt_y, nxt_m, FRIDAY, 3) - timedelta(days=30))


def deribit_monthly(year: int, month: int) -> date:
    """Last Friday of the month, settling 08:00 UTC.

    Not holiday-shifted: Deribit is a crypto venue and does not observe NYSE
    closures.
    """
    return last_weekday(year, month, FRIDAY)


def is_deribit_quarterly(day: date) -> bool:
    return day.month in QUARTER_MONTHS and day == deribit_monthly(day.year, day.month)


def cme_crypto_roll(year: int, month: int) -> date:
    """CME crypto futures final settlement — last Friday."""
    return last_weekday(year, month, FRIDAY)


def rolled_today(today: date) -> bool:
    """Did a Deribit expiry settle at 08:00 UTC, before this brief built?

    The brief dispatches at 08:20 UTC. See the module docstring: on these
    mornings the options figures have already jumped to the next expiry.
    """
    return today == deribit_monthly(today.year, today.month)


# -------------------------------------------------------------- the section

# How many days ahead each cycle starts appearing. Impact sets lead time: a
# quarterly expiry deserves a fortnight's notice, a CME roll does not.
LEADS = {
    "Triple witching": 10,
    "Monthly opex": 5,
    "VIX expiry": 3,
    "Deribit quarterly": 14,
    "Deribit monthly": 5,
    "CME crypto roll": 3,
}


def _months_ahead(today: date, count: int = 4):
    y, m = today.year, today.month
    for _ in range(count):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def upcoming(today: date) -> list[dict]:
    """Every cycle inside its own lead window, nearest first.

    A cycle outside its window is not printed. A 365-day horizon that prints
    everything floods, and a section nobody reads is worse than no section —
    the flat-list failure the tier redesign exists to fix.
    """
    found: dict[tuple[str, date], dict] = {}
    for year, month in _months_ahead(today):
        opex = monthly_opex(year, month)
        name = "Triple witching" if is_triple_witching(opex) else "Monthly opex"
        deribit = deribit_monthly(year, month)
        dname = ("Deribit quarterly" if is_deribit_quarterly(deribit)
                 else "Deribit monthly")
        for label, when, note in (
            (name, opex, "US equity options"),
            ("VIX expiry", vix_expiry(year, month), "VIX futures and options"),
            (dname, deribit, "settles 08:00 UTC"),
            ("CME crypto roll", cme_crypto_roll(year, month),
             "CME crypto futures final settlement"),
        ):
            days = (when - today).days
            if days < 0 or days > LEADS[label]:
                continue
            found.setdefault((label, when), {
                "name": label, "date": when, "days": days, "note": note})
    return sorted(found.values(), key=lambda e: (e["date"], e["name"]))
