"""# vectra.registration

Registry system utilities.
"""

__all__ =   [
                # Registries
                "COMMAND_REGISTRY",
                "SERVICE_REGISTRY",

                # Decorators
                "register_command",
                "register_service",
            ]

from vectra.registration.decorators import *
from vectra.registration.registries import *

# Instantiate registries.
COMMAND_REGISTRY:   CommandRegistry =   CommandRegistry()
SERVICE_REGISTRY:   ServiceRegistry =   ServiceRegistry()