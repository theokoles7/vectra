"""# vectra.registration.core.entry

Abstract registration entry protocol.
"""

from abc                                    import ABC
from argparse                               import _SubParsersAction
from logging                                import Logger
from typing                                 import Callable, List, Optional, Type

from vectra.configuration                   import Config
from vectra.registration.core.exceptions    import ParserNotConfiguredError
from vectra.utilities                       import get_logger

class Entry(ABC):
    """# Abstract Registration Entry"""

    def __init__(self,
        id:             str,
        config:         Optional[Type[Config]] =    None,
        entry_point:    Optional[Callable] =        None,
        tags:           List[str] =                 []
    ):
        """# Instantiate Registration Entry.

        ## Args:
            * id            (str):                  Entry identifier (seminal entity).
            * config        (Type[Config] | None):  Configuration & argument handler class.
            * entry_poijt   (Callable | None):      Main process entry point.
            * tags          (List[str]):            Taxonomical key words.
        """
        # Initialize logger.
        self.__logger__:    Logger =                    get_logger(f"{id}-entry")

        # Define properties.
        self._id_:          str =                       id
        self._tags_:        List[str] =                 tags
        self._config_:      Optional[Type[Config]] =    config
        self._entry_point_: Optional[Callable] =        entry_point

        # Debug initialization.
        self.__logger__.debug(f"Initialized {self}")

    # PROPERTIES ===================================================================================

    @property
    def config(self) -> Optional[Type[Config]]:
        """# Configuration & Argument Handler"""
        return self._config_
    
    @property
    def entry_point(self) -> Optional[Callable]:
        """# Main Process Entry Point"""
        return self._entry_point_
    
    @property
    def id(self) -> str:
        """# Entry Identifier"""
        return self._id_
    
    @property
    def tags(self) -> List[str]:
        """# Taxonomical Keywords"""
        return self._tags_
    
    # METHODS ======================================================================================

    def has_tag(self,
        tag:    str
    ) -> bool:
        """# Registration Entry Has Taxonomy Tag?

        ## Args:
            * tag   (str):  Tag being queried.

        ## Returns:
            * bool: True, if registration entry has queried tag.
        """
        # Debug tag query.
        self.__logger__.debug(f"{self} has tag {tag} = {tag in self._tags_}")

        # Query tag.
        return tag in self._tags_
    
    def register_configuration(self,
        subparser:  _SubParsersAction
    ) -> None:
        """# Register Configuration & Argument Handler.

        ## Args:
            * subparser (_SubParsersAction):    Sub-parser group of parent under which this entry's 
                                                configuration will be registered.

        ## Raises:
            * ParserNotCOnfiguredError: If entry was not registered with a configuration & argument 
                                        handler.
        """
        # If entry was not registered with a configuration, report error.
        if self.config is None: raise ParserNotConfiguredError(entry_id = self.id)

        # Debug registration.
        self.__logger__.debug(f"Registering {self} configuration under {subparser.dest}")

        # Register configuration.
        self.config.register(subparser = subparser)

    # DUNDERS ======================================================================================

    def __repr__(self) -> str:
        """# Registration Entry Object Representation"""
        return f"""<Entry(id = {self.id}, config = {self.config}, tags = {self.tags})>"""