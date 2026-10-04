"""# vectra.data.exceptions.ohlcv_validation

OHLCV validation error implementation.
"""

__all__ = ["OHLCVValidationError"]

from typing                             import List

from vectra.data.exceptions.protocol    import DataValidationError

class OHLCVValidationError(DataValidationError):
    """# OHLCV Validation Error
    
    Raised when OHLCV data or its metadata violates one or more format rules.
    """

    def __init__(self,
        violations: List[str]
    ):
        """Raise OHLCV Validation Error.

        ## Args:
            * violations    (List[str]):    Every rule violation found.
        """
        super(OHLCVValidationError, self).__init__(
            kind =          "OHLCV data",
            violations =    violations
        )