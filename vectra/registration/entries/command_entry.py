"""# vectra.registration.entries.command_entry

Command registration entry.
"""

__all__ = ["CommandEntry"]

from typing                     import Callable, Type

from vectra.configuration       import CommandConfig
from vectra.registration.core   import Entry

class CommandEntry(Entry):
    """# COmmand Registration Entry"""

    def __init__(self,
        id:             str,
        config:         Type[CommandConfig],
        entry_point:    Callable
    ):
        """# Instantiate Command Registration Entry.

        ## Args:
            * id            (str):                  Name of command/ID of command parser.
            * config        (Type[CommandConfig]):  Command's argument configuration.
            * entry_point   (Callable):             Command's main process entry point.
        """
        # Initialize entry.
        super(CommandEntry, self).__init__(id = id, config = config, entry_point = entry_point)