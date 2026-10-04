"""# vectra.data.types.timespan

Duration of candles.
"""

__all__ = ["Timespan"]

from datetime   import timedelta
from enum       import Enum
from typing     import Dict, Optional

class Timespan(Enum):
    """# Candle Duration"""

    # Minutes
    M1 =    "M1"    # 1-minute
    M5 =    "M5"    # 5-minute
    M15 =   "M15"   # 15-minute
    M30 =   "M30"   # 30-minute

    # Hours
    H1 =    "H1"    # 1-hour
    H2 =    "H2"    # 2-hour
    H4 =    "H4"    # 4-hour

    # Calendar
    D =     "D"     # Day
    W =     "W"     # Week
    MN =    "MN"    # Month

    # PROPERTIES ===================================================================================

    @property
    def delta(self) -> Optional[timedelta]:
        """# Fixed Candle Duration
        
        Duration of a single candle, or None for calendar-based timespans (weeks & months) whose 
        length varies.
        """
        return _TIMESPAN_DELTAS_[self]

    @property
    def is_intraday(self) -> bool:
        """# Timespan is Shorter Than One Day?"""
        return self.delta is not None and self.delta < timedelta(days = 1)


# DELTAS ===========================================================================================

_TIMESPAN_DELTAS_:  Dict[Timespan, timedelta] = {
                                                    Timespan.M1:    timedelta(minutes = 1),
                                                    Timespan.M5:    timedelta(minutes = 5),
                                                    Timespan.M15:   timedelta(minutes = 15),
                                                    Timespan.M30:   timedelta(minutes = 30),

                                                    Timespan.H1:    timedelta(hours = 1),
                                                    Timespan.H2:    timedelta(hours = 2),
                                                    Timespan.H4:    timedelta(hours = 4),

                                                    Timespan.D:     timedelta(days = 1),
                                                    Timespan.W:     None,
                                                    Timespan.MN:    None
                                                }