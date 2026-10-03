"""# vectra.registration.decorators

Function annotation decorators for registration of components.
"""

__all__ =   [
                "register_command",
                "register_service",
            ]

from typing                 import Callable, List, Optional, Type

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


def register_service(
    id:     str,
    config: Type["ServiceConfig"],
    tags:   Optional[List[str]] =   None
) -> Callable:
    """# Register Service.

    ## Args:
        * id        (str):                  Service identifier.
        * config    (Type[ServiceConfig]):  Service configuration handler.
        * tags      (List[str] | None):     Taxonomical descriptors. Defaults to None.

    ## Returns:
        * Callable: Service registration decorator.
    """
    # Define decorator.
    def decorator(
        service:    Type
    ) -> Type:
        """# Service Registration Decorator.

        ## Args:
            * service   (Type): Service class being registered.
        """
        # Load registry.
        from vectra.registration    import SERVICE_REGISTRY

        # Register service.
        SERVICE_REGISTRY.register(
            entry_id =  id,
            config =    config,
            service =   service,
            tags =      tags
        )

        # Expose service class.
        return service

    # Expose decorator.
    return decorator