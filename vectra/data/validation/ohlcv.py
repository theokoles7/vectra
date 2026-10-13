"""# vectra.data.validation.ohlcv

OHLCV data format validation.
"""

__all__ =   [
                "OHLCV_COLUMNS",
                "validate_ohlcv",
            ]

from datetime                           import datetime
from typing                             import Dict, FrozenSet, List, Tuple
from zoneinfo                           import ZoneInfo, ZoneInfoNotFoundError

from numpy                              import isfinite, zeros
from pandas                             import DataFrame, DatetimeIndex, Index

from vectra.data.types                  import Adjustment, Session, Timespan
from vectra.data.exceptions             import OHLCVValidationError

# Define required columns.
OHLCV_COLUMNS:      Tuple[str, ...] =       ("open", "high", "low", "close", "volume")

# Timespans whose alignment is checked as minutes-since-midnight multiples.
_MINUTE_ALIGNED_:   FrozenSet[Timespan] =   frozenset({
                                                Timespan.M1,
                                                Timespan.M5,
                                                Timespan.M15,
                                                Timespan.M30
                                            })

# Define price-valued columns.
_PRICES_:           List[str] =             ["open", "high", "low", "close"]

# PRIMARY ==========================================================================================

def validate_ohlcv(
    frame:      DataFrame,
    *,
    symbol:         str,
    timespan:       Timespan,
    sessions:       FrozenSet[Session],
    adjustment:     Adjustment,
    source:         str,
    timezone:       str,
    retrieved_at:   datetime
) -> None:
    """# Validate OHLCV Data & Metadata.

    ## Args:
        * violations    (List[str]):            OHLCV data.
        * symbol        (str):                  Uppercase ticker symbol.
        * timespan      (Timespan):             Candle duration.
        * sessions      (FrozenSet[Session]):   Sessions the data was requested to include.
        * adjustment    (Adjustment):           Corporate action price adjustment.
        * source        (str):                  Vendor from whence the data came.
        * timezone      (str):                  Exchange timezone (IANA name).
        * retrieved_at  (datetime):             Timezone-aware moment the data was retrieved.

    ## Raises:
        * OHLCVValidationError: If any rule is violated (lists every violation).
    """
    # Initialize list of violations.
    violations:     List[str] =         []

    # Validate metadata.
    exchange_tz:    ZoneInfo | None =   _check_metadata_(
                                            violations, symbol, timespan, sessions, adjustment, 
                                            source, timezone, retrieved_at
                                        )

    # Validate structure.
    if _check_structure_(violations, frame):

        # If frame is not empty...
        if len(frame) > 0:

            # Check index.
            _check_index_(violations, frame.index, timespan, sessions, exchange_tz, retrieved_at)

            # Check values.
            _check_values_(violations, frame)

    # Report all violations together.
    if violations: raise (OHLCVValidationError(violations = violations))

# VALIDATIONS ======================================================================================

def _check_metadata_(
    violations:     List[str],
    symbol:         str,
    timespan:       Timespan,
    sessions:       FrozenSet[Session],
    adjustment:     Adjustment,
    source:         str,
    timezone:       str,
    retrieved_at:   datetime
) -> ZoneInfo | None:
    """# Validate Metadata.
    
    ## Returns:
        * ZoneInfo: Exchange timezone, if metadata is valid.
    """
    # If symbol is not a non-empty string...
    if not isinstance(symbol, str) or not symbol.strip():

        # Report violation.
        violations.append(f"symbol must be a non-empty string, got {symbol!r}")

    # If symbol is not capitalized...
    elif symbol != symbol.upper():

        # Report violation.
        violations.append(f"symbol must be uppercase, got {symbol!r}")

    # If timespane was not normalized to Vectra data...
    if not isinstance(timespan, Timespan):

        # Report violation.
        violations.append(f"timespan must be a Timespan, got {timespan!r}")

    # If sessions is not frozen, non-empty set...
    if not isinstance(sessions, frozenset) or not sessions:

        # Report violation.
        violations.append(f"sessions must be non-empty frozenset, got {sessions!r}")

    # If not all sessions are Vectra-normalized sessions...
    elif not all(isinstance(session, Session) for session in sessions):

        # Report violation.
        violations.append(f"sessions must contain on Session members, got {sessions!r}")

    # If adustment is not Vectra-normalized...
    if not isinstance(adjustment, Adjustment):

        # Report violation.
        violations.append(f"adjustment must be an Adjustment, got {adjustment!r}")

    # If source is not a non-empty string...
    if not isinstance(source, str) or not source.strip():

        # Report violation.
        violations.append(f"source must be non-empty string, got {source!r}")

    # If retrieval time is not a timezone-aware datetime...
    if not isinstance(retrieved_at, datetime) or retrieved_at.utcoffset() is None:

        # Report violation.
        violations.append(f"retrieved_at must be a timezone-aware datetime, got {retrieved_at!r}")

    # Return timezone on validation success.
    try:    return ZoneInfo(timezone)

    # Otherwise...
    except (ZoneInfoNotFoundError, TypeError, ValueError):

        # Report timezone format violation & return.
        violations.append(f"timezone must be a valid IANA timezone name, got {timezone!r}"); return None

def _check_structure_(
        violations: List[str],
        frame:      DataFrame
) -> bool:
    """# Validate Columns, Data Types, & Index Type.
    
    ## Returns:
        * bool: True, if structurally sound.
    """
    # If data is not a dataframe...
    if not isinstance(frame, DataFrame):

        # Report violation & indicate validation failure.
        violations.append(f"frame must be a DataFrame, got {frame!r}"); return False

    # Initialize validation flag.
    sound:  bool =  True

    # If column names differ from Vectra-defined columns...
    if tuple(frame.columns) != OHLCV_COLUMNS:

        # Report violation.
        violations.append(f"columns must be exactly {list(OHLCV_COLUMNS)}, got {list(frame.columns)}")

        # Invalidate structure.
        sound = False

    # Also...
    else:

        # Check data types.
        wrong:  Dict[str, str] =    {c: str(t) for c, t in frame.dtypes.items() if str(t) != "float64"}

        # If any values are not float64...
        if wrong:

            # Report violation.
            violations.append(f"All columns must be float64, got {wrong}")

            # Invalidate structure.
            sound = False

    # Extract frame index.
    index:  Index = frame.index

    # If it is not datetime...
    if not isinstance(index, DatetimeIndex):

        # Report violation & and indication validation failure.
        violations.append(f"index must be DatetimeIndex, got {index!r}"); return False

    # If timezone is not UTC...
    if index.tz is None or str(index.tz) != "UTC":

        # Report violation.
        violations.append(f"index must be timezone-aware UTC, got tz={index.tz}")

        # Invalidate structure.
        sound = False

    # If candle start time is not the index...
    if index.name != "start":

        # Report violation.
        violations.append(f"""index must be named "start", got {index.name!r}""")  

    # Indicate validation result.
    return sound

def _check_index_(
        violations:     List[str],
        index:          DatetimeIndex,
        timespan:       Timespan,
        sessions:       FrozenSet[Session],
        exchange_tz:    ZoneInfo | None,
        retrieved_at:   datetime
) -> None:
    """# Validate Ordering, Alignment, Session Membership, & Retrieval Bound."""
    # If index contains any duplicates...
    if not index.is_unique:

        # Report violation.
        violations.append(f"index contains duplicate timestamps")

    # If timestamps are not monotonically increasing...
    if not index.is_monotonic_increasing:

        # Report violation.
        violations.append(f"index must be monotonically increasing")

    # If index does not start on a whole minute...
    if ((index.second != 0) | (index.microsecond != 0) | (index.nanosecond != 0)).any():

        # Report violation.
        violations.append("candles must start on whole minutes")

    # Assuming proper retrieval time...
    if isinstance(retrieved_at, datetime) and retrieved_at.utcoffset() is not None:

        # If any timestamps appeared in the future...
        if (index > retrieved_at).any():

            # Report violation.
            violations.append(f"candles start after retrieved_at ({retrieved_at.isoformat()})")  

    # Return if exchange timezone is invalid.
    if exchange_tz is None or not isinstance(timespan, Timespan): return

    # Convert timezone.
    local:          DatetimeIndex = index.tz_convert(exchange_tz)
    minute_of_day:  int =           local.hour * 60 + local.minute

    # If daily candles...
    if timespan is Timespan.D:

        # Misaligned if day does not start at zero minute.
        misaligned = minute_of_day != 0

        # If such is the case...
        if misaligned.any():

            # Report violation.
            violations.append(f"daily candles must start at 00:00")

    # Otherwise, if candle can span over midnight.
    elif timespan in _MINUTE_ALIGNED_:

        # Determine minute-size of candle(s).
        size:   int =   int(timespan.delta.total_seconds() // 60)

        # Determine if any are misaligned.
        misaligned =    (minute_of_day % size) != 0

        # If any are misaligned.
        if misaligned.any():

            # Report violation.
            violations.append(f"{timespan.value} candles must start on {size}-minute boundaries")

    # If timespan is during the trading day...
    if timespan.is_intraday and isinstance(sessions, frozenset) and sessions \
       and all(isinstance(session, Session) for session in sessions):

        # Determine interior session candles.
        inside = zeros(len(index), dtype = bool)

        # For each session within...
        for session in sessions:

            # Determine the start & end time.
            start:  int =   session.start.hour * 60 + session.start.minute
            end:    int =   session.end.hour * 60 + session.end.minute
            inside |=   ((minute_of_day >= start) | (minute_of_day < end)) if session.wraps_midnight \
                        else ((minute_of_day >= start) & (minute_of_day < end))

        # If any candles are within...  
        if (~inside).any():

            # Get their times.
            names:  List[str] = sorted(session.value for session in sessions)

            # Report violations.
            violations.append(f"candles start outside requested sessions {names}")

def _check_values_(
    violations: List[str],
    frame:      DataFrame
) -> None:
    """# Check Finiteness, Signs, & OHLC Consistency."""
    # Extract index.
    index:  DatetimeIndex = frame.index

    # Find non-finite values.
    nonfinite = ~isfinite(frame.to_numpy()).all(axis = 1)

    # If any infinite values are found...
    if nonfinite.any():  

        # Report violation.
        violations.append(f"values must be finite (no NaN/inf)")

    # Find non-positive prices.
    nonpositive = (frame[_PRICES_] <= 0).any(axis = 1).to_numpy()

    # If any non-positive prices are found...
    if nonpositive.any():

        # Report violation.
        violations.append(f"prices must be non-negative")

    # Find non-positive volume.
    negative = (frame["volume"] < 0).to_numpy()

    # If any non-positive values are found...
    if negative.any():

        # Report violation.
        violations.append(f"volume must be >= 0")

    # Extract OHLC data.
    o, h, l, c, v = (frame[column].to_numpy() for column in OHLCV_COLUMNS)

    # Check consistency.
    inconsistent:   bool =  (h < o) | (l > o) | (l > c) | (h < l) | (h < c)

    # If any inconsistencies are found...
    if inconsistent.any():

        # Report violation.
        violations.append(f"high must be >= open/close/low & low <= open/closed")