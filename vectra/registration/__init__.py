"""# vectra.registration

Registry system utilities.
"""

__all__ =   [
                # Registries
                "COMMAND_REGISTRY",

                # Decorators
                "register_command",
            ]

from vectra.registration.decorators import *
from vectra.registration.registries import *

# Instantiate registries.
COMMAND_REGISTRY:   CommandRegistry =   CommandRegistry()