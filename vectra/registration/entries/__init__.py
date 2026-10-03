"""# vectra.registration.entries

Concrete registration entry protocols.
"""

__all__ =   [
                "CommandEntry",
                "ServiceEntry",
            ]

from vectra.registration.entries.command_entry  import CommandEntry
from vectra.registration.entries.service_entry  import ServiceEntry