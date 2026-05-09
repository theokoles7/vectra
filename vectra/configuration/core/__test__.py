"""# vectra.configuration.core.test

Tests for configuration protocols, subparser mechanics, and exceptions.
"""

from argparse                               import ArgumentParser, Namespace

from pytest                                 import raises

from vectra.configuration.core.exceptions   import *
from vectra.conftest                        import ConcreteConfig, ConcreteConfigWithSubparser

# EXCEPTIONS =======================================================================================

class TestConfigurationError():
    """# Verify Generic Configuration Error Functionality."""

    def test_is_exception(self) -> None:
        """# Assert that Configuration Erro is an Exception."""
        assert  issubclass(ConfigurationError, Exception),   \
                "ConfigurationError should be type Exception"

    def test_can_raise(self) -> None:
        """# Ensure Configuration Error Can Be Raised."""
        with raises(ConfigurationError): raise ConfigurationError("Test")


class TestSubParserNotConfiguredError():
    """# Verify Sub-Parser Not Configured Error Functionality."""

    def test_is_configuration_error(self):
        """# Assert that SubParserNotConfiguredError is a ConfigurationError."""
        assert  issubclass(SubParserNotConfiguredError, ConfigurationError),    \
                "SubParserNotConfiguredError no longer inherits from ConfigurationError"

    def test_message_contains_parser_id(self):
        """# Ensure SubParserNotConfiguredError Message Contains Parser ID."""
        # Initialize error.
        err:    SubParserNotConfiguredError =   SubParserNotConfiguredError(parser_id = "test")

        # Assert that message contains "test".
        assert "test" in str(err), "Sub-parser ID no longer appears in error message"

    def test_can_raise(self):
        """# Ensure SubParserNotConfiguredError Can Be Raised."""
        with raises(SubParserNotConfiguredError): raise SubParserNotConfiguredError("test")


# CONFIG PROPERTIES ================================================================================

class TestConfigProperties():
    """# Verify Config Properties Are Defined/Accessed Properly."""

    def test_parser_id(self, config: ConcreteConfig) -> None:
        """# Test Parser ID Access."""
        assert config.parser_id == "test-parser", "Config parser ID value inaccessible or incorrect"

    def test_parser_help(self, config: ConcreteConfig) -> None:
        """# Test Parser Description Access."""
        assert  config.parser_help == "Test parser.",   \
                "Config parser description inaccessible or incorrect"

    def test_parser_is_argument_parser(self, config: ConcreteConfig) -> None:
        """# Assert Config Parser is an Argument Parser."""
        assert  isinstance(config.parser, ArgumentParser),  \
                "Config parser is no longer type ArgumentParser"

    def test_parser_prog_matches_id(self, config: ConcreteConfig) -> None:
        """# Ensure Config Parser's Prog Property Matches Config ID."""
        assert  config.parser.prog == "test-parser",    \
                "Config parser prog attribute inaccessible or incorrect"

    def test_subparser_title_none_by_default(self, config: ConcreteConfig) -> None:
        """# Ensure Sub-Parser's Title is None by Default."""
        assert  config.subparser_title is None, \
                "Config sub-parser title should be None by default"

    def test_subparser_help_none_by_default(self, config: ConcreteConfig) -> None:
        """# Ensure Sub-Parser's Description is None by Default."""
        assert  config.subparser_help is None,  \
                "Config sub-parser description should be None by default"

    def test_subparser_dest_none_when_title_absent(self, config: ConcreteConfig) -> None:
        """# Ensure Sub-Parser's Destination is None When There's No Title."""
        assert  config.subparser_dest is None,  \
                "Config sub-parser destination should be None by default"

    def test_subparser_dest_derived_from_title(self):
        """# Ensure Sub-Parser Destination is Properly Derived from Title."""
        # Create config.
        config: ConcreteConfig =    ConcreteConfig(subparser_title = "test-sub")

        # Assert that hyphens are converted to underscores.
        assert  config.subparser_dest == "test_sub",    \
                "Config sub-parser destination inaccessible or incorrect"

    def test_subparser_title_stored(self,
        config_with_subparser: ConcreteConfigWithSubparser
    ) -> None:
        """# Assert Sub-Parser Title is Stored."""
        assert  config_with_subparser.subparser_title == "test-sub",    \
                "Config sub-parser title inaccessible or incorrect"

    def test_subparser_help_stored(self,
        config_with_subparser: ConcreteConfigWithSubparser
    ) -> None:
        """# Assert Sub-Parser Description is Stored."""
        assert  config_with_subparser.subparser_help == "Test sub-command.",    \
                "Config sub-parser description inaccessible or incorrect"


# PARSING ARGUMENTS ================================================================================

class TestConfigArgumentParsing():
    """# Verify Argument Parsing Functionality."""

    def test_parse_known_returns_namespace(self, config: ConcreteConfig) -> None:
        """# Assert That Known Arguments are Returned as Namespace."""
        # Parse arguments.
        ns, leftover =  config.parse_arguments([])

        # Assert that arguments are parsed as Namespace.
        assert  isinstance(ns, Namespace),  \
                "Recognized arguments no longer returned as Namespace"

    def test_parse_known_returns_leftover_list(self, config: ConcreteConfig) -> None:
        """# Assert That Leftover Arguments are Returned as List."""
        # Parse arguments.
        ns, leftover =  config.parse_arguments(["--unknown", "value"])

        # Assert that leftover arguments are returned as list.
        assert  isinstance(leftover, list), \
                "Unrecognized arguments no longer returned as list"

        # Assert that leftover arguments are returned.
        assert "--unknown"  in leftover, "Unrecognized argument(s) do not appear in list returned"
        assert "value"      in leftover, "Unrecognized argument(s) do not appear in list returned"

    def test_defined_argument_parsed(self, config_with_args: ConcreteConfig) -> None:
        """# Assert That Recognized Arguments are Parsed into Namespace."""
        # Parse arguments.
        ns, _ = config_with_args.parse_arguments(["--foo", "hello"])

        # Assert that argument & value are parsed.
        assert ns.foo == "hello", "Recognized arguments were not parsed"

    def test_defined_argument_default(self, config_with_args: ConcreteConfig) -> None:
        """# Assert that Argument Defaults are Utilized."""
        # Parse arguments.
        ns, _ = config_with_args.parse_arguments(["--foo", "bar"])

        # Assert that argument & value are parsed.
        assert ns.foo == "bar", "Argument default value not honored"

    def test_namespace_passthrough(self, config: ConcreteConfig) -> None:
        """# Ensure Namespace Argument Pass Through."""
        # Create generic namespace.
        existing:   Namespace = Namespace(pre = "existing")

        # Parse namespace.
        ns, _ =                 config.parse_arguments([], namespace = existing)

        # Assert that pre-defined arguments still exist.
        assert ns.pre == "existing", "Namespace passthrough failed"


# SUB-PARSER CREATION ==============================================================================

class TestCreateSubparser():
    """# Verify Sub-Parser Creation."""

    def test_creates_subparsers_action(self,
        config_with_subparser:  ConcreteConfigWithSubparser
    ) -> None:
        """# Assert Sub-Parser is Created as Defined."""
        assert  config_with_subparser.subparser_dest in {
                    a.dest for a in config_with_subparser.parser._actions
                }, "Sub-Parser destination not attributed to parser"
        
    def test_raises_when_title_not_defined(self, config: ConcreteConfig) -> None:
        """# Ensure Error is Raised When Sub-Parser not Defined."""
        with raises(SubParserNotConfiguredError):
            
            # Force an error to raise.
            config._create_subparser_(parser = config.parser),  \
            "Sub-parser cannot be created when it is not defined"