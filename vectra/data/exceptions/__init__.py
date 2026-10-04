"""# vectra.data.exceptions

Market data validation exceptions module.
"""

__all__ =   [
                # Protocol
                "DataValidationError",

                # Concrete
                "OHLCVValidationError",
            ]

# Protocol
from vectra.data.exceptions.protocol    import DataValidationError

# Concrete
from vectra.data.exceptions.ohlcv       import OHLCVValidationError