"""# vectra.data.connectors.core.protocol

Abstract data connector protocol.
"""

__all__ = ["Connector"]

from abc        import ABC, abstractmethod
from datetime   import datetime
from typing     import Optional

from pandas     import DataFrame

class Connector(ABC):
    """# Abstract Data Connector"""

    def __init__(self,
        id: str
    ):
        """# Instantiate Data Connector.

        ## Args:
            * id    (str):  Data connector identifier.
        """
        from logging            import Logger
        
        from vectra.utilities   import get_logger

        # Define properties.
        self._id_:          str =       str(id)

        # Initialize logger.
        self.__logger__:    Logger =    get_logger(f"{self.id}-connector")

        # Debug initialization.
        self.__logger__.debug(f"Initialized {self}")

    # PROPERTIES ===================================================================================

    @property
    def id(self) -> str:
        """# Data Connector Identifier"""
        return self._id_
    
    # METHODS ======================================================================================

    @abstractmethod
    def fetch(self,
        ticker:     str,
        interval:   str,
        range:      Optional[str] =         None,
        start:      Optional[datetime] =    None,
        end:        Optional[datetime] =    None
    ) -> DataFrame:
        """# Fetch Market Data.

        ## Args:
            * ticker    (str):              Stock's ticker symbol.
            * interval  (str):              Time interval.
            * range     (str | None):       Time range. Defaults to None.
            * start     (datetime | None):  Start date of data. Defaults to None.
            * end       (datetime | None):  End date of data. Defaults to None.

        ## Returns:
            * DataFrame:    OHLCV market data.
        """
        ...
    
    # DUNDERS ======================================================================================

    def __repr__(self) -> str:
        """# Data Connector Object Representation"""
        return f"""<Connector(id = {self.id})>"""