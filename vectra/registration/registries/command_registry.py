"""# vectra.registration.registries.command_registry

Command registry system.
"""

__all__ = ["CommandRegistry"]

from typing                         import override

from vectra.registration.core       import Registry
from vectra.registration.entries    import CommandEntry

class CommandRegistry(Registry[CommandEntry]):
    """# Command Registration System"""

    def __init__(self):
        """# Instantiate Command Registration System."""
        super(CommandRegistry, self).__init__(id = "commands")
    
    # HELPERS ======================================================================================

    @override
    def _create_entry_(self, **kwargs) -> CommandEntry:
        """# Create Command Entry."""
        return CommandEntry(**kwargs)