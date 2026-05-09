"""# vectra.args

Arguments definitions & parsing for Vectra application.
"""

__all__ = ["parse_vectra_arguments"]

from argparse               import _ArgumentGroup, ArgumentParser, Namespace, _SubParsersAction
from typing                 import Optional, Sequence

from vectra.registration    import COMMAND_REGISTRY

def parse_vectra_arguments(
    args:       Optional[Sequence[str]] =   None,
    namespace:  Optional[Namespace] =       None
) -> Namespace:
    """# Parse Vectra Arguments.

    ## Args:
        * args      (Sequence[str] | None): Sequence of string/system arguments.
        * namespace (Namespace | None):     Mapping of arguments to their values.

    ## Returns:
        * Namespace:    Mapping of arguments & their values.
    """
    # Initialize parser.
    parser:     ArgumentParser =    ArgumentParser(
                                        prog =          "vectra",
                                        description =   """Experiments in algorithmic trading via 
                                                        machine learning solutions."""
                                    )
    
    # Initialize sub-parser.
    subparser:  _SubParsersAction = parser.add_subparsers(
                                        title =         "vectra-command",
                                        dest =          "vectra_command",
                                        help =          """Vectra command being executed.""",
                                        description =   """Vectra command being executed."""
                                    )
    
    # LOGGING ======================================================================================
    logging:    _ArgumentGroup =    parser.add_argument_group(
                                        title = "Logging",
                                        description =   """Logging utility configuration."""
                                    )
    
    logging.add_argument(
        "--logging-level",
        dest =      "logging_level",
        type =      str,
        choices =   ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"],
        default =   "INFO",
        help =      """Minimal logging level (DEBUG < INFO < WARNING < ERROR < CRITICAL). Defaults 
                    to "INFO"."""
    )

    logging.add_argument(
        "--logging-path",
        dest =      "logging_path",
        type =      str,
        default =   "logs",
        help =      """Path at which logs will be written. Defaults to "./logs/"."""
    )

    logging.add_argument(
        "--debug",
        dest =      "logging_level",
        action =    "store_const",
        const =     "DEBUG",
        help =      """Set logging level to DEBUG."""
    )

    # ==============================================================================================

    # Register commands.
    COMMAND_REGISTRY.register_configurations(subparser = subparser)

    # Parse arguments.
    return parser.parse_args(args, namespace)