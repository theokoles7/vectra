"""# vectra.data.series.ohlcv

OHLCV candle series implementation.
"""
__all__ = ["OHLCVSeries"]

from dataclasses                    import dataclass, field, replace
from datetime                       import datetime
from typing                         import Any, Dict, FrozenSet, Union

from pandas                         import DataFrame, Timestamp

from vectra.data.types              import Adjustment, Session, Timespan
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