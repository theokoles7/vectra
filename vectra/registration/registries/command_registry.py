"""# vectra.registration.registries.command_registry

Command registry system.
"""

__all__ = ["CommandRegistry"]

from typing                         import Any, Dict, override

from vectra.registration.core       import Registry
from vectra.registration.entries    import CommandEntry

class CommandRegistry(Registry):
    """# Command Registration System"""

    def __init__(self):
        """# Instantiate Comand Registration System."""
        super(CommandRegistry, self).__init__(id = "commands")

    # PROPERTIES ===================================================================================

    @override
    @property
    def entries(self) -> Dict[str, CommandEntry]:
        """# Registered Command Entries"""
        return self._entries_.copy()
    
    # HELPERS ======================================================================================

    @override
    def _create_entry_(self, **kwargs) -> CommandEntry:
        """# Create Command Entry."""
        return CommandEntry(**kwargs)
    
    # DUNDERS ======================================================================================

    @override
    def __getitem__(self,
        command_id: str
    ) -> CommandEntry:
        """# Query Registered Commands.

        ## Args:
            * command_id    (str):  Identifier of command being queried.

        ## Raises:
            * EntryNotFoundError:   If command queried is not registered.

        ## Returns:
            * CommandEntry: Command entry, if registered.
        """
        return self.get_entry(entry_id = command_id)