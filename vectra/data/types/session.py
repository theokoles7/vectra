"""# vectra.data.types.session

Trading session data type implementation.
"""

__all__ = ["Session"]

from datetime   import time
from enum       import Enum
from typing     import Dict

class Session(Enum):
    """# Trading Session
    
    Session hours are expressed in exchange-level time (US equities: America/New_York). Each session 
    includes its start time & excludes its end time.
    """
    PRE =       "PRE"
    REGULAR =   "REGULAR"
    POST =      "POST"
    OVERNIGHT = "OVERNIGHT"

    # PROPERTIES ===================================================================================

    @property
    def end(self) -> time:
        """# Session End (Exchange-Local, Exclusive)"""
        return _SESSION_HOURS_[self]["end"]

    @property
    def start(self) -> time:
        """# Session Start (Exchange-Level, Inclusive)"""
        return _SESSION_HOURS_[self]["start"]

    @property
    def wraps_midnight(self) -> bool:
        """# Session Spans Midnight?"""
        return self.end < self.start

    # METHODS ======================================================================================

    def contains(self,
        moment: time
    ) -> bool:
        """# Session Contains Time of Day?
        
        ## Args:
            * moment    (time): Exchange-local time of day being queried.

        ## Returns:
            * bool: True, if moment falls within this session's hours.
        """
        # Sessions spanning midnight contain times after their start OR before their end.
        if self.wraps_midnight: return moment >= self.start or moment < self.end

        # All other sessions contain times between their start & end.
        return self.start <= moment < self.end


# HOURS ============================================================================================

_SESSION_HOURS_:    Dict[Session, Dict[str, time]] =    {
                                                            Session.PRE:        {
                                                                                    "start":    time(4, 0),
                                                                                    "end":      time(9, 30)
                                                                                },
                                                            Session.REGULAR:    {
                                                                                    "start":    time(9, 30),
                                                                                    "end":      time(16, 0)
                                                                                },
                                                            Session.POST:       {
                                                                                    "start":    time(16, 0),
                                                                                    "end":      time(20, 0)
                                                                                },
                                                            Session.OVERNIGHT:  {
                                                                                    "start":    time(20, 0),
                                                                                    "end":      time(4, 0)
                                                                                }
                                                        }