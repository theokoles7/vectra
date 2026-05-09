"""# vectra.registratin.core

Core registration components.
"""

__all__ =   [
                # Protocols
                "Entry",
                "Registry",

                # Exceptions
                "DuplicateEntryError",
                "EntryNotFoundError",
                "EntryPointNotConfiguredError",
                "ParserNotConfiguredError",
                "RegistrationError",
                "RegistryNotLoadedError"
            ]

from vectra.registration.core.entry         import Entry
from vectra.registration.core.exceptions    import *
from vectra.registration.core.registry      import Registry