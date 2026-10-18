"""# vectra.data.exceptions.protocol

Generic data validation error protocol.
"""

__all__ = ["DataValidationError"]

from typing import List

class DataValidationError(Exception):
    """# Generic Data Validation Error
    
    Base exception class for all market data validation errors.
    """

    def __init__(self,
        kind:       str,
        violations: List[str]
    ):
        """Raise Data Validation Error.

        ## Args:
            * kind          (str):          Kind of data that failed validation.
            * violations    (List[str]):    Every rule violation found.
        """
        # Define properties.
        self.violations:    List[str] = list(violations)

        # Compose message listing every violation.
        super(DataValidationError, self).__init__(
            f"""{kind} failed validation ({len(self.violations)} violation(s)):\n"""
            + "\n".join(f" - {violation}" for violation in self.violations)
        )