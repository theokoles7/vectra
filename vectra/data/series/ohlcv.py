"""# vectra.data.series.ohlcv

OHLCV candle series implementation.
"""
__all__ = ["OHLCVSeries"]

from dataclasses                    import dataclass, field, replace
from datetime                       import datetime, timedelta
from typing                         import Any, Dict, FrozenSet, Union

from pandas                         import concat as concat_frames, DataFrame, Timestamp

from vectra.data.types              import Adjustment, MINUTE_TIMESPANS, Session, Timespan
from vectra.data.validation.ohlcv   import validate_ohlcv

@dataclass(frozen = True, eq = False)
class OHLCVSeries():
    """# OHLCV Candle Series
    
    Validated, immutable OHLCV candles for one symbol, plus the metadata describing them.
    """

    frame:          DataFrame =         field(repr = False)
    symbol:         str
    timespan:       Timespan
    sessions:       FrozenSet[Session]
    adjustment:     Adjustment
    source:         str
    retrieved_at:   datetime
    timezone:       str =               "America/New_York"

    def __post_init__(self) -> None:
        """# Validate & Detach Frame From Caller"""
        # Validate frame & metadata.
        validate_ohlcv(frame = self.frame, **self.metadata)

        # Store a copy so later changes to the caller's frame cannot bypass validation.
        object.__setattr__(self, "frame", self.frame.copy())

    # PROPERTIES ===================================================================================

    @property
    def metadata(self) -> Dict[str, Any]:
        """# Series Metadata"""
        return  {
                    "symbol":       self.symbol,
                    "timespan":     self.timespan,
                    "sessions":     self.sessions,
                    "adjustment":   self.adjustment,
                    "source":       self.source,
                    "retrieved_at": self.retrieved_at,
                    "timezone":     self.timezone
                }

    # METHODS ======================================================================================

    def between(self,
        start:  Union[datetime, str],
        end:    Union[datetime, str]
    ) -> "OHLCVSeries":
        """# Select Candles Starting Within [start, end).

        ## Args:
            * start (datetime | str):   Inclusive lower bound (timezone-aware).
            * end   (datetime | str):   Exclusive upper bound (timezone-aware).

        ## Raises:
            * ValueError:   If either bound is timezone-naive.

        ## Returns:
            * OHLCVSeries:  New series with the same metadata.
        """
        # Parse bounds.
        lower, upper =  Timestamp(start), Timestamp(end)

        # If timestamps are naive/ambiguous...
        if lower.tzinfo is None or upper.tzinfo is None:

            # Refuse to proceed.
            raise ValueError(f"bounds must be timezone-aware, got {start!r}, {end!r}")

        # Select candles.
        return  replace(self, frame = self.frame[
                    (self.frame.index >= lower) & (self.frame.index < upper)
                ])

    @classmethod
    def concat(cls,
        *series:    "OHLCVSeries"
    ) -> "OHLCVSeries":
        """# Join Series of Identical Metadata Into One.

        Overlapping candles must be identical; they are kept once. The result's retrieval time is 
        the latest of the inputs.

        ## Args:
            * series    (OHLCVSeries):  Series to join (any order).

        ## Raises:
            * ValueError:   If no series are provided, metadata differs (other than retrieval 
                            time), or overlapping candles differ.

        ## Returns:
            * OHLCVSeries:  Joined series.
        """
        # Require at least one series.
        if not series: raise ValueError("concat() requires at least one series")

        # Extract the first series.
        first:  OHLCVSeries =   series[0]

        # For each other series provided...
        for other in series[1:]:

            # Find differing fields.
            differing:  list =  [
                                    key for key, value in first.metadata.items()
                                    if key != "retrieved_at" and other.metadata[key] != value
                                ]

            # Refuse to mix differing series.
            if differing: raise ValueError(f"cannot concat series with differing {differing}")

        # Stack & sort candles.
        frame:      DataFrame = concat_frames([s.frame for s in series]).sort_index()

        # Find any overlapping candles.
        overlap =   frame.index.duplicated(keep = False)

        # If there are any overlapping candles that don't contain the exact same data...
        if (frame[overlap].groupby(level = 0).nunique() > 1).any().any():

            # Report error.
            raise ValueError("cannot concat series whose overlapping candles differ")

        # Keep one copy of each candle; carry the latest retrieval time.
        return  replace(
                    first,
                    frame =         frame[~frame.index.duplicated(keep = "first")],
                    retrieved_at =  max(s.retrieved_at for s in series)
                )

    def resample(self,
        timespan:   Timespan
    ) -> "OHLCVSeries":
        """# Aggregate Candles Into a Larger Timespan.

        Supports minute -> minute (whole multiples) & minute -> daily. Daily candles are grouped 
        by exchange-local session date.

        ## Args:
            * timespan  (Timespan): Target candle duration.

        ## Raises:
            * ValueError:   If the target is unsupported, not larger, or not a whole multiple, or 
                            if daily grouping would split the overnight session.

        ## Returns:
            * OHLCVSeries:  Resampled series with the same metadata (except timespan).
        """
        # If this is not a minute-timespan...
        if self.timespan not in MINUTE_TIMESPANS:

            # Report that only minute timespans are supported for now.
            raise ValueError(f"resample() supports minute sources only, got {self.timespan.value}")

        # If target is daily...
        if timespan is Timespan.D:

            # Calendar-date grouping would split the overnight session across two days.
            if Session.OVERNIGHT in self.sessions:
                raise ValueError("cannot resample OVERNIGHT session candles to daily")

            # Group by exchange-local midnight of each candle's date.
            keys =  self.frame.index.tz_convert(self.timezone).normalize().tz_convert("UTC")

        # Otherwise, if target is a larger whole multiple of the source...
        elif timespan in MINUTE_TIMESPANS and timespan.delta > self.timespan.delta \
             and timespan.delta % self.timespan.delta == timedelta(0):

            # Group by target boundary (exchange offsets are whole hours, so UTC flooring aligns).
            keys =  self.frame.index.floor(timespan.delta)

        # Otherwise, refuse.
        else: raise ValueError(f"cannot resample {self.timespan.value} to {timespan.value}")

        # Aggregate each group into one candle.
        frame:  DataFrame = self.frame.groupby(keys).agg({
                                "open":     "first",
                                "high":     "max",
                                "low":      "min",
                                "close":    "last",
                                "volume":   "sum",
                            })

        # Restore index name & return new series.
        return replace(self, frame = frame.rename_axis("start"), timespan = timespan)

    # DUNDERS ======================================================================================

    def __len__(self) -> int:
        """# Number of Candles"""
        return len(self.frame)

    def __repr__(self) -> str:
        """# OHCLV Series Object Representation"""
        # Notate span.
        span:   str =   f"{self.frame.index[0]} -> {self.frame.index[-1]}" if len(self) else "empty"

        # Return object representation.
        return  (
                    f"<OHLCVSeries({self.symbol}, {self.timespan.value}, {len(self)} candles, "
                    f"{span}, {self.adjustment.value}, {self.source})>"
                )