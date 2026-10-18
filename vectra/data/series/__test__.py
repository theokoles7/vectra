"""# vectra.data.series.test

Tests for OHLCV candle series.
"""

from dataclasses            import FrozenInstanceError
from datetime               import datetime, timezone
from typing                 import Any, Dict, List

from pandas                 import DataFrame, DatetimeIndex, Timestamp
from pytest                 import fixture, raises

from vectra.data.exceptions import OHLCVValidationError
from vectra.data.series     import OHLCVSeries
from vectra.data.types      import Adjustment, Session, Timespan

# FIXTURES =========================================================================================

# Raw Webull daily candles (newest first, string-typed), as returned by the sandbox.
WEBULL_DAILY:   List[Dict[str, str]] =  [
    {"time": "2026-10-02T04:00:00.000+0000", "open": "333.260000", "close": "333.690000",
     "high": "334.540000", "low": "330.610000", "volume": "33278552", "trading_session": ""},
    {"time": "2026-10-01T04:00:00.000+0000", "open": "330.000000", "close": "330.320000",
     "high": "332.481600", "low": "325.810000", "volume": "36306346", "trading_session": ""},
    {"time": "2026-09-30T04:00:00.000+0000", "open": "330.80", "close": "333.02",
     "high": "339.50", "low": "330.1401", "volume": "49988558", "trading_session": ""},
]

RETRIEVED_AT:   datetime =  datetime(2026, 10, 4, 14, 35, tzinfo = timezone.utc)


def webull_frame(candles: List[Dict[str, str]]) -> DataFrame:
    """# Convert Raw Webull Candles to a Standard OHLCV Frame (Stand-In for the Service)."""
    frame:  DataFrame = DataFrame(candles)
    frame.index = DatetimeIndex(frame.pop("time"), name = "start").tz_convert("UTC")
    return frame[["open", "high", "low", "close", "volume"]].astype("float64").sort_index()


@fixture
def metadata() -> Dict[str, Any]:
    """# Metadata for Webull Daily AAPL Candles"""
    return  {
                "symbol":       "AAPL",
                "timespan":     Timespan.D,
                "sessions":     frozenset({Session.REGULAR}),
                "adjustment":   Adjustment.ALL,
                "source":       "webull",
                "retrieved_at": RETRIEVED_AT,
            }


@fixture
def series(metadata: Dict[str, Any]) -> OHLCVSeries:
    """# Valid Webull Daily AAPL Series"""
    return OHLCVSeries(frame = webull_frame(WEBULL_DAILY), **metadata)


# CONSTRUCTION =====================================================================================

class TestConstruction():
    """# Verify Construction Validates & Isolates Data."""

    def test_webull_daily_fixture_is_valid(self, series: OHLCVSeries) -> None:
        """# Assert Real Webull Daily Candles Convert to a Valid Series."""
        assert  len(series) == 3,   \
                "Series should contain all 3 Webull candles"

    def test_candles_sorted_oldest_first(self, series: OHLCVSeries) -> None:
        """# Assert Newest-First Webull Candles End Up Oldest-First."""
        assert  series.frame.index[0] == Timestamp("2026-09-30T04:00:00Z"), \
                "First candle should be the oldest"

    def test_default_timezone(self, series: OHLCVSeries) -> None:
        """# Assert Exchange Timezone Defaults to New York."""
        assert  series.timezone == "America/New_York",  \
                "Timezone should default to America/New_York"

    def test_invalid_frame_rejected(self, metadata: Dict[str, Any]) -> None:
        """# Assert Construction Runs Validation."""
        with raises(OHLCVValidationError):
            OHLCVSeries(frame = webull_frame(WEBULL_DAILY).iloc[::-1], **metadata)

    def test_invalid_metadata_rejected(self, metadata: Dict[str, Any]) -> None:
        """# Assert Construction Validates Metadata."""
        with raises(OHLCVValidationError):
            OHLCVSeries(frame = webull_frame(WEBULL_DAILY), **{**metadata, "symbol": "aapl"})

    def test_caller_frame_changes_do_not_leak(self, metadata: Dict[str, Any]) -> None:
        """# Assert Mutating the Caller's Frame After Construction Leaves the Series Unchanged."""
        frame:  DataFrame =     webull_frame(WEBULL_DAILY)
        series: OHLCVSeries =   OHLCVSeries(frame = frame, **metadata)
        frame.iloc[0, 0] = -1.0
        assert  series.frame.iloc[0, 0] > 0,    \
                "Series should hold its own copy of the frame"


# IMMUTABILITY =====================================================================================

class TestImmutability():
    """# Verify Series Fields Cannot be Reassigned."""

    def test_fields_are_frozen(self, series: OHLCVSeries) -> None:
        """# Assert Fields Cannot be Reassigned."""
        with raises(FrozenInstanceError):
            series.symbol = "MSFT"


# METADATA =========================================================================================

class TestMetadata():
    """# Verify Metadata Access."""

    def test_metadata_excludes_frame(self, series: OHLCVSeries, metadata: Dict[str, Any]) -> None:
        """# Assert Metadata Holds Every Field Except the Frame."""
        assert  series.metadata == {**metadata, "timezone": "America/New_York"},  \
                "Metadata should contain every non-frame field"


# BETWEEN ==========================================================================================

class TestBetween():
    """# Verify Time-Range Selection."""

    def test_inclusive_start_exclusive_end(self, series: OHLCVSeries) -> None:
        """# Assert Selection Includes Start & Excludes End."""
        selected:   OHLCVSeries =   series.between("2026-09-30T04:00:00Z", "2026-10-02T04:00:00Z")
        assert  list(selected.frame.index) == [Timestamp("2026-09-30T04:00:00Z"),
                                               Timestamp("2026-10-01T04:00:00Z")],  \
                "between() should include start & exclude end"

    def test_bounds_in_other_timezones(self, series: OHLCVSeries) -> None:
        """# Assert Bounds in Any Timezone are Compared as Instants."""
        # 2026-10-01 00:00 New York == 2026-10-01T04:00Z.
        selected:   OHLCVSeries =   series.between("2026-10-01T00:00:00-04:00", "2026-10-03T00:00:00-04:00")
        assert  len(selected) == 2, \
                "Bounds should be converted to UTC before comparing"

    def test_preserves_metadata(self, series: OHLCVSeries) -> None:
        """# Assert Selection Returns a Series with Identical Metadata."""
        selected:   OHLCVSeries =   series.between("2026-01-01T00:00:00Z", "2027-01-01T00:00:00Z")
        assert  selected.metadata == series.metadata,   \
                "between() should preserve metadata"

    def test_empty_selection_is_valid(self, series: OHLCVSeries) -> None:
        """# Assert Selecting No Candles Yields a Valid Empty Series."""
        assert  len(series.between("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z")) == 0,  \
                "Empty selection should yield an empty series"

    def test_naive_bounds_rejected(self, series: OHLCVSeries) -> None:
        """# Assert Timezone-Naive Bounds are Rejected."""
        with raises(ValueError):
            series.between("2026-09-30", "2026-10-02")


# DUNDERS ==========================================================================================

class TestDunders():
    """# Verify Series Dunder Methods."""

    def test_repr_summarizes(self, series: OHLCVSeries) -> None:
        """# Assert __repr__ Summarizes Without Dumping the Frame."""
        text:   str =   repr(series)
        assert  "AAPL" in text and "3 candles" in text and "webull" in text and "open" not in text, \
                "__repr__ should summarize the series without printing candles"

    def test_repr_empty(self, series: OHLCVSeries) -> None:
        """# Assert __repr__ Handles Empty Series."""
        assert  "empty" in repr(series.between("2025-01-01T00:00:00Z", "2025-01-02T00:00:00Z")),    \
                "__repr__ should mark empty series"

# CONCAT ===========================================================================================

def minute_series(
    starts:         List[str],
    closes:         List[float],
    retrieved_at:   datetime =  RETRIEVED_AT,
    **overrides
) -> OHLCVSeries:
    """# Build a Regular-Hours 1-Minute AAPL Series (One Candle per Start, Flat at Each Close)."""
    frame:  DataFrame = DataFrame(
                            data =      [(c, c, c, c, 10.0) for c in closes],
                            columns =   ["open", "high", "low", "close", "volume"],
                            index =     DatetimeIndex(starts, tz = "UTC", name = "start"),
                            dtype =     "float64"
                        )
    return  OHLCVSeries(**{
                "frame":        frame,
                "symbol":       "AAPL",
                "timespan":     Timespan.M1,
                "sessions":     frozenset({Session.REGULAR}),
                "adjustment":   Adjustment.NONE,
                "source":       "test",
                "retrieved_at": retrieved_at,
                **overrides
            })


def replace_frame(series: OHLCVSeries, frame: DataFrame) -> OHLCVSeries:
    """# Rebuild a Series With a Different Frame (Revalidated)."""
    return OHLCVSeries(frame = frame, **series.metadata)


# 2026-10-02 is EDT (UTC-4): 09:30 New York == 13:30Z.
MINUTES:    List[str] = [f"2026-10-02T13:{m}:00Z" for m in range(30, 40)]


class TestConcat():
    """# Verify Joining Series."""

    def test_joins_and_sorts_pages(self) -> None:
        """# Assert Pages Given Out of Order are Joined Oldest-First."""
        later:      OHLCVSeries =   minute_series(MINUTES[5:], [6.0, 7.0, 8.0, 9.0, 10.0])
        earlier:    OHLCVSeries =   minute_series(MINUTES[:5], [1.0, 2.0, 3.0, 4.0, 5.0])
        joined:     OHLCVSeries =   OHLCVSeries.concat(later, earlier)
        assert  list(joined.frame["close"]) == [float(i) for i in range(1, 11)],  \
                "concat() should join pages in time order"

    def test_identical_overlap_kept_once(self) -> None:
        """# Assert Identical Overlapping Candles Appear Once."""
        a:  OHLCVSeries =   minute_series(MINUTES[:3], [1.0, 2.0, 3.0])
        b:  OHLCVSeries =   minute_series(MINUTES[2:5], [3.0, 4.0, 5.0])
        assert  len(OHLCVSeries.concat(a, b)) == 5, \
                "Identical overlapping candle should be kept once"

    def test_differing_overlap_rejected(self) -> None:
        """# Assert Overlapping Candles That Differ are Rejected."""
        a:  OHLCVSeries =   minute_series(MINUTES[:3], [1.0, 2.0, 3.0])
        b:  OHLCVSeries =   minute_series(MINUTES[2:5], [99.0, 4.0, 5.0])
        with raises(ValueError, match = "overlapping"):
            OHLCVSeries.concat(a, b)

    def test_differing_metadata_rejected(self) -> None:
        """# Assert Series with Different Metadata Cannot be Joined."""
        raw:        OHLCVSeries =   minute_series(MINUTES[:3], [1.0, 2.0, 3.0])
        adjusted:   OHLCVSeries =   minute_series(MINUTES[3:6], [4.0, 5.0, 6.0], adjustment = Adjustment.ALL)
        with raises(ValueError, match = "adjustment"):
            OHLCVSeries.concat(raw, adjusted)

    def test_latest_retrieval_time_kept(self) -> None:
        """# Assert Joined Series Carries the Latest Retrieval Time."""
        later:  datetime =      datetime(2026, 10, 5, tzinfo = timezone.utc)
        joined: OHLCVSeries =   OHLCVSeries.concat(minute_series(MINUTES[:3], [1.0, 2.0, 3.0]),
                                                   minute_series(MINUTES[3:6], [4.0, 5.0, 6.0], later))
        assert  joined.retrieved_at == later,   \
                "concat() should keep the latest retrieval time"

    def test_requires_series(self) -> None:
        """# Assert Joining Nothing is Rejected."""
        with raises(ValueError):
            OHLCVSeries.concat()


# RESAMPLE =========================================================================================

class TestResample():
    """# Verify Aggregation Into Larger Timespans."""

    def test_minute_to_five_minute_aggregation(self) -> None:
        """# Assert 1-Minute Candles Aggregate Correctly Into 5-Minute Candles."""
        frame:  DataFrame = DataFrame(
                                data =      [(10.0, 12.0, 9.0, 11.0, 1.0),
                                             (11.0, 15.0, 10.0, 14.0, 2.0),
                                             (14.0, 14.0, 8.0, 9.0, 3.0)],
                                columns =   ["open", "high", "low", "close", "volume"],
                                index =     DatetimeIndex(MINUTES[:3], tz = "UTC", name = "start"),
                                dtype =     "float64"
                            )
        series: OHLCVSeries =   minute_series(MINUTES[:1], [1.0])
        five:   OHLCVSeries =   replace_frame(series, frame).resample(Timespan.M5)
        assert  five.frame.iloc[0].tolist() == [10.0, 15.0, 8.0, 9.0, 6.0], \
                "open=first, high=max, low=min, close=last, volume=sum"

    def test_groups_on_boundaries(self) -> None:
        """# Assert 10 One-Minute Candles From 09:30 Form Two 5-Minute Candles (09:30, 09:35)."""
        five:   OHLCVSeries =   minute_series(MINUTES, [float(i) for i in range(1, 11)]).resample(Timespan.M5)
        assert  list(five.frame.index) == [Timestamp(MINUTES[0]), Timestamp(MINUTES[5])],   \
                "5-minute candles should start on 5-minute boundaries"

    def test_metadata_preserved_except_timespan(self) -> None:
        """# Assert Resampling Changes Only the Timespan."""
        series: OHLCVSeries =   minute_series(MINUTES, [1.0] * 10)
        five:   OHLCVSeries =   series.resample(Timespan.M5)
        assert  five.metadata == {**series.metadata, "timespan": Timespan.M5},   \
                "Only the timespan should change"

    def test_minute_to_daily_across_dst_change(self) -> None:
        """# Assert Daily Candles Group by New York Date Across a DST Change."""
        # 09:30 New York: 13:30Z on 2026-10-30 (EDT), 14:30Z on 2026-11-02 (EST).
        series: OHLCVSeries =   minute_series(["2026-10-30T13:30:00Z", "2026-10-30T19:59:00Z",
                                               "2026-11-02T14:30:00Z"], [1.0, 2.0, 3.0],
                                              datetime(2026, 11, 3, tzinfo = timezone.utc))
        daily:  OHLCVSeries =   series.resample(Timespan.D)
        assert  list(daily.frame.index) == [Timestamp("2026-10-30T04:00:00Z"),
                                            Timestamp("2026-11-02T05:00:00Z")],   \
                "Daily candles should start at New York midnight on each session date"

    def test_daily_rejects_overnight(self) -> None:
        """# Assert Overnight Session Candles Cannot be Grouped Into Calendar Days."""
        # 01:00 New York == 05:00Z.
        series: OHLCVSeries =   minute_series(["2026-10-02T05:00:00Z"], [1.0],
                                              sessions = frozenset({Session.OVERNIGHT}))
        with raises(ValueError, match = "OVERNIGHT"):
            series.resample(Timespan.D)

    def test_not_larger_rejected(self) -> None:
        """# Assert Resampling to the Same or a Smaller Timespan is Rejected."""
        five:   OHLCVSeries =   minute_series(MINUTES, [1.0] * 10).resample(Timespan.M5)
        for target in (Timespan.M5, Timespan.M1):
            with raises(ValueError):
                five.resample(target)

    def test_unsupported_targets_rejected(self) -> None:
        """# Assert Hourly, Weekly, & Monthly Targets are Not Yet Supported."""
        series: OHLCVSeries =   minute_series(MINUTES, [1.0] * 10)
        for target in (Timespan.H1, Timespan.W, Timespan.MN):
            with raises(ValueError):
                series.resample(target)

    def test_non_minute_source_rejected(self, series: OHLCVSeries) -> None:
        """# Assert Daily Sources Cannot be Resampled Yet."""
        with raises(ValueError):
            series.resample(Timespan.W)