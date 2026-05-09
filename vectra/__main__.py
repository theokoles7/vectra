"""# vectra.main

Primary application process.
"""

__all__ = ["vectra_entry_point"]

from typing import Any

def vectra_entry_point(*args, **kwargs) -> Any:
    """# Execute Vectra Command.

    ## Returns:
        * Any:  Data returned from sub-process(es).
    """
    from argparse               import Namespace
    from logging                import Logger

    from vectra.__args__        import parse_vectra_arguments
    from vectra.registration    import COMMAND_REGISTRY
    from vectra.utilities       import configure_logger

    # Parse arguments.
    arguments:  Namespace = parse_vectra_arguments(*args, **kwargs)

    # Initialize logger.
    logger:     Logger =    configure_logger(
                                logging_level = arguments.logging_level,
                                logging_path =  arguments.logging_path
                            )
    
    # Debug arguments.
    logger.debug(f"Vectra arguments: {vars(arguments)}")

    try:# Dispatch to command.
        COMMAND_REGISTRY.dispatch(entry_id = arguments.vectra_command, **vars(arguments))

    # Catch wildcard errors.
    except Exception as e:  logger.critical(f"Unexpected error: {e}", exc_info = True)

    # Exit gracefully.
    finally:                logger.debug(f"Exiting...")

if __name__ == "__main__": vectra_entry_point()