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