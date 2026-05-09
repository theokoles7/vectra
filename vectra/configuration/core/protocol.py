"""# vectra.configuration.core.protocol

Abstract configuration and argument handling protocol.
"""

__all__ = ["Config"]

from abc                                    import ABC, abstractmethod
from argparse                               import ArgumentParser, Namespace, _SubParsersAction
from functools                              import cached_property
from typing                                 import List, Optional, Sequence, Tuple, Type

from vectra.configuration.core.exceptions   import SubParserNotConfiguredError

class Config(ABC):
    """# Abstract Configuration & Argument Handler"""

    def __init__(self,
        parser_id:          str,
        parser_help:        str,
        subparser_title:    Optional[str] = None,
        subparser_help:     Optional[str] = None
    ):
        """# Instantiate Configuration & Argument Handler.

        ## Args:
            * parser_id         (str):          Parser/Program name.
            * parser_help       (str):          Parser/Program description.
            * subparser_title   (str | None):   Sub-Parser ID/Title. Defaults to None.
            * subparser_help    (str | None):   Sub-Parser description. Defaults to None.
        """
        # Define properties.
        self._parser_id_:       str =               parser_id
        self._parser_help_:     str =               parser_help
        self._subparser_title_: Optional[str] =     subparser_title
        self._subparser_help_:  Optional[str] =     subparser_help
        
        # Define arguments.
        self._define_arguments_(parser = self.parser)

    # PROPERTIES ===================================================================================

    @cached_property
    def parser(self) -> ArgumentParser:
        """# Configuration Argument Parser"""
        return  ArgumentParser(prog = self.parser_id, description = self.parser_help)
    
    @property
    def parser_help(self) -> str:
        """# Parser/Program Description"""
        return self._parser_help_
    
    @property
    def parser_id(self) -> str:
        """# Parser/Program Identifier"""
        return self._parser_id_
    
    @cached_property
    def subparser_dest(self) -> Optional[str]:
        """# Sub-Parser Destination Variable"""
        return self.subparser_title.replace("-", "_") if self.subparser_title else None
    
    @property
    def subparser_help(self) -> Optional[str]:
        """# Sub-Parser Description"""
        return self._subparser_help_
    
    @property
    def subparser_title(self) -> Optional[str]:
        """# Sub-Parser ID/Title"""
        return self._subparser_title_
    
    # METHODS ======================================================================================

    def parse_arguments(self,
        args:       Optional[Sequence[str]] =   None,
        namespace:  Optional[Namespace] =       None
    ) -> Tuple[Namespace, List[str]]:
        """# Parse Defined Arguments.

        ## Args:
            * args      (Sequence[str] | None): Sequence of system arguments.
            * namespace (Namespace | None):     Previously parsed arguments name space.

        ## Returns:
            * Namespace:    Name spaec of arguments/values that were known by the parser.
            * List[str]:    Sequence of leftover argument strings that were not recognized by the 
                            parser.
        """
        # Parse known arguments, but provide leftovers for continuity of sub-systems.
        return self.parser.parse_known_args(args = args, namespace = namespace)
    
    @classmethod
    def register(
        cls:        Type["Config"],
        subparser:  _SubParsersAction
    ) -> ArgumentParser:
        """# Register Configuration Parser as Sub-Command.

        ## Args:
            * cls       (Type[Config]):         This configuration class, being registered as 
                                                sub-command under parent.
            * subparser (_SubParsersAction):    Sub-parser group of parent under which this 
                                                configuration will be registered.

        ## Returns:
            * ArgumentParser:   New argument parser, representing new sub-command.
        """
        # Instantiate this configuration class to expose properties.
        config: Config =            cls()

        # Register this configuration as a sub-command under the sub-parser group provided.
        parser: ArgumentParser =    subparser.add_parser(
                                        name =          config.parser_id,
                                        help =          config.parser_help,
                                        description =   config.parser_help
                                    )
        
        # Define this configuration's arguments under new parser.
        config._define_arguments_(parser = parser)

        # Expose new parser.
        return parser
    
    # HELPERS ======================================================================================
    
    def _create_subparser_(self,
        parser: ArgumentParser
    ) -> _SubParsersAction:
        """# Create Sub-Parser Group.

        ## Args:
            * parser    (ArgumentParser):   Parser to whom sub-parser will be attributed.

        ## Raises:
            * SubParserNotConfiguredError:  If sub-parser properties are not defined.

        ## Returns:
            * _SubParsersAction:    New sub-parser group.
        """
        # If sub-parser properties are not defined...
        if self.subparser_title is None:

            # Report error.
            raise SubParserNotConfiguredError(parser_id = self.parser_id)
        
        # Create sub-parser.
        return  parser.add_subparsers(
                    title =         self.subparser_title,
                    dest =          self.subparser_dest,
                    help =          self.subparser_help,
                    description =   self.subparser_help
                )
    
    @abstractmethod
    def _define_arguments_(self,
        parser: ArgumentParser
    ) -> None:
        """# Define Configuration Arguments.

        Override this function to define any arguments for configuration of attributable class and 
        create sub-parser when necessary.

        ## Args:
            * parser    (ArgumentParser):   Parser to whom arguments will be attributed.
        
        ## Define Arguments:
            >>> parser.add_argument(...)

        ## Create Sub-Parser:
            >>> self._create_subparser_(parser = parser)
        """
        pass