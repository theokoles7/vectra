"""# vectra.data.connectors.yfinance

Yahoo Finance data connector.
"""

__all__ = ["YFinance"]

from datetime                       import datetime
from typing                         import Optional, override

from pandas                         import DataFrame

from vectra.data.connectors.core    import Connector

class YFinance(Connector):
    """# Yahoo Finance Data Connector"""

    def __init__(self):
        """# Instantiate Yahoo Finance Data Connector."""
        # Initialize connector.
        super(YFinance, self).__init__(id = "yfinance")

    