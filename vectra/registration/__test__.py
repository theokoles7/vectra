"""# vectra.registration.test

Tests for the register_command decorator and COMMAND_REGISTRY singleton.
"""

from pytest                                 import raises

from vectra.registration                    import COMMAND_REGISTRY
from vectra.registration.decorators         import register_command
from vectra.registration.registries         import CommandRegistry
from vectra.registration.core.exceptions    import DuplicateEntryError

from vectra.conftest                        import ConcreteConfig


# HELPERS ==========================================================================================

def _unique_id(base: str, _counter: list = [0]) -> str:
    """Return a unique command ID to prevent cross-test DuplicateEntryError on the singleton."""
    _counter[0] += 1; return f"{base}-{_counter[0]}"


# COMMAND REGISTRY SINGLETON =======================================================================

class TestCommandRegistrySingleton():
    """# Verify COMMAND_REGISTRY Singleton Behavior."""

    def test_is_command_registry_instance(self) -> None:
        """# Assert COMMAND_REGISTRY is a CommandRegistry Instance."""
        assert  isinstance(COMMAND_REGISTRY, CommandRegistry), \
                "COMMAND_REGISTRY is no longer a CommandRegistry instance"

    def test_same_object_on_repeated_import(self) -> None:
        """# Assert COMMAND_REGISTRY is the Same Object Across Imports."""
        from vectra.registration import COMMAND_REGISTRY as CR2
        assert  COMMAND_REGISTRY is CR2,    \
                "COMMAND_REGISTRY is not the same object across imports"

    def test_registry_id_is_commands(self) -> None:
        """# Assert COMMAND_REGISTRY ID is 'commands'."""
        assert  COMMAND_REGISTRY.id == "commands",  \
                "COMMAND_REGISTRY ID inaccessible or incorrect"


# REGISTER COMMAND DECORATOR =======================================================================

class TestRegisterCommandDecorator():
    """# Verify register_command Decorator Behavior."""

    def test_entry_point_returned_unchanged(self) -> None:
        """# Assert register_command Returns the Entry Point Unchanged."""
        cmd_id: str =   _unique_id("ret-test")

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _command(**kwargs): return "ok"

        assert  _command() == "ok", \
                "register_command did not return the entry point unchanged"

    def test_entry_is_registered_in_command_registry(self) -> None:
        """# Assert Decorated Command Appears in COMMAND_REGISTRY."""
        cmd_id: str =   _unique_id("reg-test")

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _command(**kwargs): pass

        assert  cmd_id in COMMAND_REGISTRY,     \
                "Decorated command not found in COMMAND_REGISTRY after registration"

    def test_registered_entry_has_correct_config(self) -> None:
        """# Assert Registered Entry Carries the Provided Config Class."""
        cmd_id: str =   _unique_id("cfg-test")

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _command(**kwargs): pass

        assert  COMMAND_REGISTRY.get_entry(cmd_id).config is ConcreteConfig,   \
                "Registered entry does not carry the provided config class"

    def test_registered_entry_point_is_callable(self) -> None:
        """# Assert Registered Entry Point is Callable."""
        cmd_id: str =   _unique_id("ep-test")

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _command(**kwargs): return "dispatched"

        assert  callable(COMMAND_REGISTRY.get_entry(cmd_id).entry_point),  \
                "Registered entry point is no longer callable"

    def test_dispatch_via_registry_calls_entry_point(self) -> None:
        """# Assert Dispatching via COMMAND_REGISTRY Calls the Entry Point."""
        cmd_id: str =   _unique_id("dispatch-test")

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _command(**kwargs): return "called"

        result  =   COMMAND_REGISTRY.dispatch(entry_id = cmd_id)
        assert  result == "called", \
                "Dispatching via COMMAND_REGISTRY did not call the entry point"

    def test_kwargs_forwarded_to_entry_point(self) -> None:
        """# Assert Keyword Arguments are Forwarded to Entry Point on Dispatch."""
        cmd_id:     str =   _unique_id("kwargs-test")
        received:   dict =  {}

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _command(**kwargs): received.update(kwargs)

        COMMAND_REGISTRY.dispatch(entry_id = cmd_id, foo = "bar", num = 42)
        assert  received["foo"] == "bar",   \
                "Keyword argument 'foo' not forwarded to entry point"
        assert  received["num"] == 42,      \
                "Keyword argument 'num' not forwarded to entry point"

    def test_duplicate_registration_raises(self) -> None:
        """# Assert Registering a Duplicate Command ID Raises DuplicateEntryError."""
        cmd_id: str =   _unique_id("dup-test")

        @register_command(id = cmd_id, config = ConcreteConfig)
        def _first(**kwargs): pass

        with raises(DuplicateEntryError):
            @register_command(id = cmd_id, config = ConcreteConfig)
            def _second(**kwargs): pass