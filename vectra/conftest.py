"""# vectra.conftest

Shared fixtures & concrete test doubles for Vectra test suite.
"""

from argparse                   import ArgumentParser
from typing                     import Optional, override

from vectra.configuration       import Config
from vectra.registration.core   import Entry, Registry

# CONCRETE DOUBLES =================================================================================

class ConcreteConfig(Config):
    """# Minimal Concrete Config for Testing Abstract Base Behavior."""

    def __init__(self,
        parser_id:          str =           "test-parser",
        parser_help:        str =           "Test parser.",
        subparser_title:    Optional[str] = None,
        subparser_help:     Optional[str] = None,
        extra_args:         bool =          False
    ):
        # Define properties.
        self._extra_args_:  bool =  extra_args

        # Initialize config.
        super(ConcreteConfig, self).__init__(
            parser_id =         parser_id,
            parser_help =       parser_help,
            subparser_title =   subparser_title,
            subparser_help =    subparser_help
        )

    @override
    def _define_arguments_(self,
        parser: ArgumentParser
    ) -> None:
        # If extra arguments are requested...
        if self._extra_args_:

            # Add an argument.
            parser.add_argument(
                "--foo",
                dest =      "foo",
                type =      str,
                default =   "bar"
            )


class ConcreteConfigWithSubparser(ConcreteConfig):
    """# Config Double that Exposes a Sub-Parser."""

    def __init__(self):
        # Initialize config.
        super(ConcreteConfigWithSubparser, self).__init__(
            subparser_title =   "test-sub",
            subparser_help =    "Test sub-command."
        )

    @override
    def _define_arguments_(self,
        parser: ArgumentParser
    ) -> None:
        # Create sub-parser.
        self._create_subparser_(parser = parser)


class ConcreteEntry(Entry):
    """# Minimal Concrete Entry for Testing Abstract Base Behavior."""
    pass


class ConcreteRegistry(Registry):
    """# Minimal Concrete Registry that Creates ConcreteEntry Instances."""

    def __init__(self):
        # Initialize registry.
        super(ConcreteRegistry, self).__init__(id = "test")

    @override
    def _create_entry_(self, **kwargs) -> ConcreteEntry:
        # Create entry.
        return ConcreteEntry(**kwargs)
    
    @override
    def _load_all_(self) -> None:
        # Skip real module importing in tests and simply flip flag.
        self._loaded_:  bool =  True