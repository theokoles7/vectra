"""# vectra.configuration.core.exceptions

Configuration & arguemnt handling exceptions/errors.
"""

__all__ =   [
                # Generic
                "ConfigurationError",

                # Concrete
                "SubParserNotConfiguredError",
            ]

# GENERIC ==========================================================================================

class ConfigurationError(Exception):
    """# Generic Configuration Error
    
    Base exception class for all configuration-related errors.
    """
    pass

# CONCRETE =========================================================================================

class SubParserNotConfiguredError(ConfigurationError):
    """# Sub-Parser Not Configured Error
    
    Raised when attempting to create a sub-parser group within a configuration class whose 
    sub-parser parameters are not defined.
    """

    def __init__(self,
        parser_id:  str
    ):
        """# Instantiate SubParserNotConfiguredError.

        ## Args:
            * parser_id (str):  Identifier of entity for whom the configuration class is defined.
        """
        super(SubParserNotConfiguredError, self).__init__(
            f"""Sub-parser parameters not defined for {parser_id} config class"""
        )