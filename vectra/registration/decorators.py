"""# vectra.registratin.decorators

Function annotation decorators for registration of components.
"""

__all__ =   [
                "register_command",
            ]

from typing                 import Callable, Type

from vectra.configuration   import *

def register_command(
    id:     str,
    config: Type["CommandConfig"]
) -> Callable:
    """# Register Command.
    
    ## Args:
        * id        (str):                  Command identifier/parser ID.
        * config    (Type[CommandConfig]):  Command's configuration & argument handler class.

    ## Returns:
        * Callable: Registration decorator.
    """
    # Define decorator.
    def decorator(
        entry_point:    Callable
    ) -> Callable:
        """# Command Registration Decorator.

        ## Arg & Return:
            * entry_point   (Callable): Command's main process entry point.
        """
        # Load registry.
        from vectra.registration    import COMMAND_REGISTRY

        # Register command.
        COMMAND_REGISTRY.register(
            entry_id =      id,
            config =        config,
            entry_point =   entry_point
        )

        # Expose entry point.
        return entry_point
    
    # Expose decorator.
    return decorator