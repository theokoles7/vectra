"""# vectra.configuration

Configuration & argument handling protocols.
"""

__all__ =   [
                # Protocol
                "Config",

                # Concrete
                "CommandConfig",
                "ServiceConfig",
            ]

from vectra.configuration.core              import Config

from vectra.configuration.command_config    import CommandConfig
from vectra.configuration.service_config    import ServiceConfig