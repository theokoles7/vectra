"""# vectra.configuration.core

Core configuration components.
"""

__all__ =   [
                # Protocol
                "Config"

                # Exceptions
                "ConfigurationError",
                "SubParserNotConfiguredError",
            ]

from vectra.configuration.core.exceptions   import *
from vectra.configuration.core.protocol     import Config