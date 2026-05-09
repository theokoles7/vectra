"""# vectra.configuration

Configuration & argument handling protocols.
"""

__all__ =   [
                # Protocol
                "Config",

                # Concrete
                "CommandConfig",
            ]

from vectra.configuration.command_config    import CommandConfig
from vectra.configuration.core              import Config