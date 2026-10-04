"""# vectra.data.core.test

Tests for vendor-neutral market data types.
"""

from datetime           import time, timedelta

from pytest             import mark

from vectra.data.types  import Adjustment, Session, Timespan

# TIMESPAN =========================================================================================

class TestTimespan():
    """# Verify Timespan Durations & Classification."""

    @mark.parametrize("timespan, delta", [
        (Timespan.M1,   timedelta(minutes = 1)),
        (Timespan.M5,   timedelta(minutes = 5)),
        (Timespan.M15,  timedelta(minutes = 15)),
        (Timespan.M30,  timedelta(minutes = 30)),
        (Timespan.H1,   timedelta(hours = 1)),
        (Timespan.H2,   timedelta(hours = 2)),
        (Timespan.H4,   timedelta(hours = 4)),
        (Timespan.D,    timedelta(days = 1)),
    ])
    def test_fixed_delta(self, timespan: Timespan, delta: timedelta) -> None:
        """# Assert Fixed Timespans Report Their Duration."""
        assert  timespan.delta == delta,    \
                f"{timespan} duration incorrect"

    @mark.parametrize("timespan", [Timespan.W, Timespan.MN])
    def test_calendar_delta_is_none(self, timespan: Timespan) -> None:
        """# Assert Calendar-Based Timespans Have No Fixed Duration."""
        assert  timespan.delta is None, \
                f"{timespan} should have no fixed duration"

    def test_every_member_has_delta_entry(self) -> None:
        """# Assert Every Timespan Defines a Duration (or Explicit None)."""
        for timespan in Timespan: timespan.delta

    @mark.parametrize("timespan", [Timespan.M1, Timespan.M5, Timespan.M15, Timespan.M30,
                                   Timespan.H1, Timespan.H2, Timespan.H4])
    def test_intraday(self, timespan: Timespan) -> None:
        """# Assert Sub-Daily Timespans Are Intraday."""
        assert  timespan.is_intraday,   \
                f"{timespan} should be intraday"

    @mark.parametrize("timespan", [Timespan.D, Timespan.W, Timespan.MN])
    def test_not_intraday(self, timespan: Timespan) -> None:
        """# Assert Daily & Longer Timespans Are Not Intraday."""
        assert  not timespan.is_intraday,   \
                f"{timespan} should not be intraday"

    def test_minute_and_month_are_distinct(self) -> None:
        """# Assert Minute & Month Timespans Cannot be Confused."""
        assert  Timespan("M1") is Timespan.M1 and Timespan("MN") is Timespan.MN,   \
                "Minute & month timespans should be distinct values"


# SESSION ==========================================================================================

class TestSession():
    """# Verify Session Hours & Membership."""

    @mark.parametrize("session, start, end", [
        (Session.PRE,       time(4, 0),     time(9, 30)),
        (Session.REGULAR,   time(9, 30),    time(16, 0)),
        (Session.POST,      time(16, 0),    time(20, 0)),
        (Session.OVERNIGHT, time(20, 0),    time(4, 0)),
    ])
    def test_hours(self, session: Session, start: time, end: time) -> None:
        """# Assert Session Hours Match Exchange Definitions."""
        assert  (session.start, session.end) == (start, end),   \
                f"{session} hours incorrect"

    def test_only_overnight_wraps_midnight(self) -> None:
        """# Assert Only the Overnight Session Spans Midnight."""
        assert  [s for s in Session if s.wraps_midnight] == [Session.OVERNIGHT],    \
                "Only OVERNIGHT should span midnight"

    @mark.parametrize("session, moment, expected", [
        (Session.REGULAR,   time(9, 30),    True),          # Start is inclusive.
        (Session.REGULAR,   time(15, 59),   True),
        (Session.REGULAR,   time(16, 0),    False),         # End is exclusive.
        (Session.REGULAR,   time(9, 29),    False),
        (Session.PRE,       time(4, 0),     True),
        (Session.PRE,       time(9, 30),    False),
        (Session.POST,      time(16, 0),    True),
        (Session.POST,      time(20, 0),    False),
        (Session.OVERNIGHT, time(20, 0),    True),
        (Session.OVERNIGHT, time(23, 59),   True),          # Before midnight.
        (Session.OVERNIGHT, time(0, 0),     True),          # After midnight.
        (Session.OVERNIGHT, time(3, 59),    True),
        (Session.OVERNIGHT, time(4, 0),     False),
        (Session.OVERNIGHT, time(12, 0),    False),
    ])
    def test_contains(self, session: Session, moment: time, expected: bool) -> None:
        """# Assert Session Membership Honors Inclusive Start & Exclusive End."""
        assert  session.contains(moment) is expected,   \
                f"{session}.contains({moment}) should be {expected}"

    def test_sessions_partition_the_day(self) -> None:
        """# Assert Every Minute of the Day Belongs to Exactly One Session."""
        for minute in range(24 * 60):
            moment:     time =  time(minute // 60, minute % 60)
            owners:     list =  [s for s in Session if s.contains(moment)]
            assert  len(owners) == 1,   \
                    f"{moment} belongs to {owners}; expected exactly one session"


# ADJUSTMENT =======================================================================================

class TestAdjustment():
    """# Verify Adjustment Members."""

    def test_members(self) -> None:
        """# Assert Adjustment Defines Exactly NONE, SPLITS, & ALL."""
        assert  {a.value for a in Adjustment} == {"NONE", "SPLITS", "ALL"}, \
                "Adjustment members changed"