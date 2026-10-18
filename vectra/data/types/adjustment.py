"""# vectra.data.types.adjustment

Corporate action price adjustment data type implementation.
"""

__all__ = ["Adjustment"]

from enum   import Enum

class Adjustment(Enum):
    """# Corporate Action Price Adjustment"""

    NONE =      "NONE"      # Raw traded prices.
    SPLITS =    "SPLITS"    # Split-adjusted only.
    ALL =       "ALL"       # Split- & dividend-adjusted.