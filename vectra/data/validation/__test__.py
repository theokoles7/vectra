"""# vectra.data.validation.test

Tests for OHLCV data validation (one passing & one failing case per rule).
"""

from datetime                           import datetime, timezone
from typing                             import Any, Dict, List, Optional, Sequence

from numpy                              import inf, nan
from pandas                             import DataFrame, DatetimeIndex
from pytest                             import fixture, mark, raises

from vectra.data.types                  import Adjustment, Session, Timespan
from vectra.data.exceptions             import DataValidationError, OHLCVValidationError
from vectra.data.validation.ohlcv       import OHLCV_COLUMNS, validate_ohlcv

# HELPERS ==========================================================================================

# A valid candle: open, high, low, close, volume.
VALID_ROW:  tuple = (100.0, 101.0, 99.0, 100.5, 1000.0)


def make_frame(
    starts: Sequence[str],
    rows:   Optional[List[tuple]] = None
) -> DataFrame:
    """# Build an OHLCV Frame Indexed by UTC Candle Starts (ISO Strings)."""
    return  DataFrame(
                data =      rows if rows is not None else [VALID_ROW] * len(starts),
                columns =   list(OHLCV_COLUMNS),
                index =     DatetimeIndex(starts, tz = "UTC", name = "start"),
                dtype =     "float64"
            )


def violations_of(frame: DataFrame, **overrides) -> List[str]:
    """# Validate & Return Violations (Empty List if Valid)."""
    metadata:   Dict[str, Any] =    {**METADATA, **overrides}
    try:                            validate_ohlcv(frame, **metadata); return []
    except OHLCVValidationError as e: return e.violations


# Valid metadata for regular-hours 1-minute AAPL candles, retrieved after all test data.
METADATA:   Dict[str, Any] =    {
                                    "symbol":       "AAPL",
                                    "timespan":     Timespan.M1,
                                    "sessions":     frozenset({Session.REGULAR}),
                                    "adjustment":   Adjustment.NONE,
                                    "source":       "test",
                                    "timezone":     "America/New_York",
                                    "retrieved_at": datetime(2027, 1, 1, tzinfo = timezone.utc),
                                }

# 2026-10-02 is EDT (UTC-4): 09:30 New York == 13:30Z.
REGULAR_STARTS: List[str] =     ["2026-10-02T13:30:00Z", "2026-10-02T13:31:00Z", "2026-10-02T13:32:00Z"]


@fixture
def frame() -> DataFrame:
    """# Valid Regular-Hours 1-Minute Frame"""
    return make_frame(REGULAR_STARTS)


# VALID DATA =======================================================================================

class TestValidData():
    """# Verify Valid Data Passes."""

    def test_valid_intraday_passes(self, frame: DataFrame) -> None:
        """# Assert Valid 1-Minute Regular-Hours Data Passes."""
        assert  violations_of(frame) == [], \
                "Valid intraday data should pass"

    def test_valid_daily_across_dst_change_passes(self) -> None:
        """# Assert Daily Candles Pass Across a DST Change (23/25-Hour UTC Gaps)."""
        # DST ends 2026-11-01: midnight New York is 04:00Z before, 05:00Z after.
        daily:  DataFrame = make_frame(["2026-10-30T04:00:00Z", "2026-11-02T05:00:00Z"])
        assert  violations_of(daily, timespan = Timespan.D) == [],  \
                "Daily candles at New York midnight should pass across DST changes"

    def test_empty_frame_passes(self) -> None:
        """# Assert Structurally Sound Empty Data Passes (3)."""
        assert  violations_of(make_frame([])) == [],    \
                "Empty data should be valid"

    def test_flat_candle_passes(self) -> None:
        """# Assert a Candle with Identical OHLC Values Passes."""
        flat:   DataFrame = make_frame(REGULAR_STARTS[:1], [(100.0, 100.0, 100.0, 100.0, 0.0)])
        assert  violations_of(flat) == [],  \
                "Flat candle with zero volume should pass"


# STRUCTURE (1, 2) =================================================================================

class TestStructure():
    """# Verify Column, Dtype, & Index Structure Rules."""

    def test_not_a_dataframe(self) -> None:
        """# Assert Non-DataFrame Input is Rejected."""
        assert  any("DataFrame" in v for v in violations_of([1, 2, 3])),  \
                "Non-DataFrame input should be rejected"

    def test_wrong_column_order(self, frame: DataFrame) -> None:
        """# Assert Reordered Columns are Rejected."""
        assert  any("columns" in v for v in violations_of(frame[["close", "open", "high", "low", "volume"]])), \
                "Columns out of order should be rejected"

    def test_extra_column(self, frame: DataFrame) -> None:
        """# Assert Extra Columns are Rejected."""
        assert  any("columns" in v for v in violations_of(frame.assign(vwap = 100.0))),   \
                "Extra columns should be rejected"

    def test_non_float_dtype(self, frame: DataFrame) -> None:
        """# Assert Non-float64 Columns are Rejected."""
        assert  any("float64" in v for v in violations_of(frame.astype({"volume": "int64"}))),    \
                "Non-float64 columns should be rejected"

    def test_non_datetime_index(self, frame: DataFrame) -> None:
        """# Assert Non-Datetime Index is Rejected."""
        assert  any("DatetimeIndex" in v for v in violations_of(frame.reset_index(drop = True))),  \
                "Non-datetime index should be rejected"

    def test_naive_index(self, frame: DataFrame) -> None:
        """# Assert Timezone-Naive Index is Rejected."""
        assert  any("UTC" in v for v in violations_of(frame.tz_localize(None))),    \
                "Naive index should be rejected"

    def test_non_utc_index(self, frame: DataFrame) -> None:
        """# Assert Non-UTC Index is Rejected (Even if Exchange-Local)."""
        assert  any("UTC" in v for v in violations_of(frame.tz_convert("America/New_York"))),    \
                "Non-UTC index should be rejected"

    def test_index_name(self, frame: DataFrame) -> None:
        """# Assert Index Must be Named 'start'."""
        assert  any("start" in v for v in violations_of(frame.rename_axis("time"))),  \
                "Index not named 'start' should be rejected"


# INDEX (4 - 8) ====================================================================================

class TestIndex():
    """# Verify Ordering, Alignment, Session, & Retrieval Rules."""

    def test_duplicate_timestamps(self) -> None:
        """# Assert Duplicate Timestamps are Rejected (4)."""
        dupes:  DataFrame = make_frame([REGULAR_STARTS[0], REGULAR_STARTS[0]])
        assert  any("duplicate" in v for v in violations_of(dupes)),  \
                "Duplicate timestamps should be rejected"

    def test_decreasing_timestamps(self) -> None:
        """# Assert Out-of-Order Timestamps are Rejected (4)."""
        unsorted:   DataFrame = make_frame(list(reversed(REGULAR_STARTS)))
        assert  any("increasing" in v for v in violations_of(unsorted)),  \
                "Out-of-order timestamps should be rejected"

    def test_fractional_minute(self) -> None:
        """# Assert Starts Off Whole Minutes are Rejected (5)."""
        assert  any("whole minutes" in v for v in violations_of(make_frame(["2026-10-02T13:30:15Z"]))), \
                "Starts with seconds should be rejected"

    def test_daily_not_at_exchange_midnight(self) -> None:
        """# Assert Daily Candles Off Exchange Midnight are Rejected (6)."""
        # 00:00Z is 20:00 the previous day in New York.
        assert  any("00:00" in v for v in violations_of(make_frame(["2026-10-02T00:00:00Z"]),
                                                        timespan = Timespan.D)), \
                "Daily candle at UTC midnight should be rejected"

    def test_minute_alignment_passes(self) -> None:
        """# Assert 5-Minute Candles on 5-Minute Boundaries Pass (6)."""
        aligned:    DataFrame = make_frame(["2026-10-02T13:30:00Z", "2026-10-02T13:35:00Z"])
        assert  violations_of(aligned, timespan = Timespan.M5) == [],  \
                "Aligned 5-minute candles should pass"

    def test_minute_misalignment(self) -> None:
        """# Assert 5-Minute Candles Off 5-Minute Boundaries are Rejected (6)."""
        misaligned: DataFrame = make_frame(["2026-10-02T13:32:00Z"])
        assert  any("boundaries" in v for v in violations_of(misaligned, timespan = Timespan.M5)),   \
                "Misaligned 5-minute candle should be rejected"

    def test_outside_requested_session(self) -> None:
        """# Assert Pre-Market Candle is Rejected When Only REGULAR Requested (7)."""
        # 12:00Z is 08:00 New York (pre-market).
        assert  any("sessions" in v for v in violations_of(make_frame(["2026-10-02T12:00:00Z"]))),  \
                "Pre-market candle should be rejected for REGULAR-only data"

    def test_inside_extended_sessions_passes(self) -> None:
        """# Assert Pre-Market Candle Passes When PRE is Requested (7)."""
        extended:   frozenset = frozenset({Session.PRE, Session.REGULAR})
        assert  violations_of(make_frame(["2026-10-02T12:00:00Z"]), sessions = extended) == [], \
                "Pre-market candle should pass when PRE is requested"

    def test_overnight_after_midnight_passes(self) -> None:
        """# Assert Overnight Candle After Midnight Passes for OVERNIGHT (7)."""
        # 05:00Z is 01:00 New York.
        overnight:  frozenset = frozenset({Session.OVERNIGHT})
        assert  violations_of(make_frame(["2026-10-02T05:00:00Z"]), sessions = overnight) == [], \
                "Overnight candle after midnight should pass"

    def test_daily_exempt_from_session_hours(self) -> None:
        """# Assert Session-Hours Rule Applies Only to Intraday Candles (7)."""
        assert  violations_of(make_frame(["2026-10-02T04:00:00Z"]), timespan = Timespan.D) == [], \
                "Daily candles at 00:00 should not be checked against session hours"

    def test_start_after_retrieval(self, frame: DataFrame) -> None:
        """# Assert Candles Starting After retrieved_at are Rejected (8)."""
        early:  datetime =  datetime(2026, 10, 2, 13, 31, tzinfo = timezone.utc)
        assert  any("retrieved_at" in v for v in violations_of(frame, retrieved_at = early)),   \
                "Candles after retrieval should be rejected"


# VALUES (9 - 12) ==================================================================================

class TestValues():
    """# Verify Value Rules."""

    @mark.parametrize("bad", [nan, inf])
    def test_non_finite(self, bad: float) -> None:
        """# Assert NaN & Infinite Values are Rejected (9)."""
        frame:  DataFrame = make_frame(REGULAR_STARTS[:1], [(100.0, 101.0, 99.0, 100.5, bad)])
        assert  any("finite" in v for v in violations_of(frame)),    \
                f"{bad} should be rejected"

    def test_non_positive_price(self) -> None:
        """# Assert Zero Prices are Rejected (10)."""
        frame:  DataFrame = make_frame(REGULAR_STARTS[:1], [(0.0, 1.0, 0.0, 0.5, 10.0)])
        assert  any("prices" in v for v in violations_of(frame)),  \
                "Zero price should be rejected"

    def test_negative_volume(self) -> None:
        """# Assert Negative Volume is Rejected (11)."""
        frame:  DataFrame = make_frame(REGULAR_STARTS[:1], [(100.0, 101.0, 99.0, 100.5, -1.0)])
        assert  any("volume" in v for v in violations_of(frame)),  \
                "Negative volume should be rejected"

    @mark.parametrize("row", [
        (100.0, 100.4, 99.0, 100.5, 1.0),       # High below close.
        (100.0, 101.0, 100.2, 100.5, 1.0),      # Low above open.
        (100.0, 99.0, 101.0, 100.0, 1.0),       # High below low.
    ])
    def test_inconsistent_ohlc(self, row: tuple) -> None:
        """# Assert Internally Inconsistent Candles are Rejected (12)."""
        assert  any("high must be" in v for v in violations_of(make_frame(REGULAR_STARTS[:1], [row]))), \
                f"Inconsistent candle {row} should be rejected"


# METADATA (13) ====================================================================================

class TestMetadata():
    """# Verify Metadata Rules."""

    @mark.parametrize("field, value, fragment", [
        ("symbol",          "aapl",                         "uppercase"),
        ("symbol",          "",                             "symbol"),
        ("timespan",        "M1",                           "Timespan"),
        ("sessions",        {Session.REGULAR},              "frozenset"),
        ("sessions",        frozenset(),                    "frozenset"),
        ("sessions",        frozenset({"REGULAR"}),         "Session"),
        ("adjustment",      "NONE",                         "Adjustment"),
        ("source",          "",                             "source"),
        ("timezone",        "Mars/Olympus_Mons",            "timezone"),
        ("retrieved_at",    datetime(2027, 1, 1),           "timezone-aware"),
    ])
    def test_invalid_metadata(self, frame: DataFrame, field: str, value: Any, fragment: str) -> None:
        """# Assert Each Invalid Metadata Field is Rejected."""
        assert  any(fragment in v for v in violations_of(frame, **{field: value})),   \
                f"Invalid {field}={value!r} should be rejected"


# REPORTING ========================================================================================

class TestReporting():
    """# Verify Violations are Collected & Reported."""

    def test_collects_every_violation(self) -> None:
        """# Assert All Violations are Reported Together, Not Just the First."""
        frame:  DataFrame = make_frame(REGULAR_STARTS[:2], [(100.0, 101.0, 99.0, 100.5, -1.0),
                                                            (0.0, 1.0, 0.0, 0.5, 1.0)])
        assert  len(violations_of(frame, symbol = "aapl")) == 3,    \
                "Symbol, volume, & price violations should all be reported"

    def test_error_hierarchy(self, frame: DataFrame) -> None:
        """# Assert OHLCVValidationError is a DataValidationError Listing Violations."""
        with raises(DataValidationError) as error:
            validate_ohlcv(frame, **{**METADATA, "symbol": "aapl"})
        assert  isinstance(error.value, OHLCVValidationError) and "uppercase" in str(error.value),  \
                "Error should be an OHLCVValidationError whose message lists violations"