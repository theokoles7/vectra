"""# vectra.registration.registries

Concrete registry systems.
"""

__all__ =   [
                "CommandRegistry",
                "ServiceRegistry",
            ]

from vectra.registration.registries.command_registry    import CommandRegistry
from vectra.registration.registries.service_registry    import ServiceRegistry