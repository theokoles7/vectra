"""# vectra.configuration.service_config

Service configuration and argument handling protocol.
"""

__all__ = ["ServiceConfig"]

from typing                             import Optional

from vectra.configuration.core.protocol import Config

class ServiceConfig(Config):
    """# Service Configuration & Argument Handler"""

    def __init__(self,
        name:               str,
        help:               str,
        subparser_title:    Optional[str] = None,
        subparser_help:     Optional[str] = None
    ):
        """# Instantiate Service Configuration & Argument Handler.

        ## Args:
            * name              (str):          Service identifier.
            * help              (str):          Description of service.
            * subparser_title   (str | None):   Name attributed to sub-command objects.
            * subparser_help    (str | None):   Description of sub-command purpose.
        """
        # Initialize configuration.
        super(ServiceConfig, self).__init__(
            parser_id =         name,
            parser_help =       help,
            subparser_title =   subparser_title,
            subparser_help =    subparser_help
        )