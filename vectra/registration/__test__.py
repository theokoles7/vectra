"""# vectra.registration.test

Tests for the register_command decorator and COMMAND_REGISTRY singleton.
"""

from pytest                                 import raises

from vectra.registration                    import COMMAND_REGISTRY, SERVICE_REGISTRY
from vectra.registration.decorators         import register_command, register_service
from vectra.registration.entries            import ServiceEntry
from vectra.registration.registries         import CommandRegistry, ServiceRegistry
from vectra.registration.core.exceptions    import DuplicateEntryError, EntryNotFoundError

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


# SERVICE REGISTRY SINGLETON =======================================================================

class TestServiceRegistrySingleton():
    """# Verify SERVICE_REGISTRY Singleton Behavior."""

    def test_is_service_registry_instance(self) -> None:
        """# Assert SERVICE_REGISTRY is a ServiceRegistry Instance."""
        assert  isinstance(SERVICE_REGISTRY, ServiceRegistry), \
                "SERVICE_REGISTRY is no longer a ServiceRegistry instance"

    def test_same_object_on_repeated_import(self) -> None:
        """# Assert SERVICE_REGISTRY is the Same Object Across Imports."""
        from vectra.registration import SERVICE_REGISTRY as CR2
        assert  SERVICE_REGISTRY is CR2,    \
                "SERVICE_REGISTRY is not the same object across imports"

    def test_registry_id_is_services(self) -> None:
        """# Assert SERVICE_REGISTRY ID is 'services'."""
        assert  SERVICE_REGISTRY.id == "services",  \
                "SERVICE_REGISTRY ID inaccessible or incorrect"


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
            
# REGISTER SERVICE DECORATOR =======================================================================
class TestRegisterServiceDecorator():
    """# Verify register_service Decorator Behavior."""

    def test_service_class_returned_unchanged(self) -> None:
        """# Assert register_service Returns the Service Class Unchanged."""
        svc_id: str =   _unique_id("svc-ret-test")

        class _Service():
            def ping(self) -> str: return "pong"

        decorated   =   register_service(id = svc_id, config = ConcreteConfig)(_Service)

        assert  decorated is _Service,          \
                "register_service did not return the service class unchanged"
        assert  decorated().ping() == "pong",   \
                "Service class no longer behaves as defined after registration"

    def test_entry_is_registered_in_service_registry(self) -> None:
        """# Assert Decorated Service Appears in SERVICE_REGISTRY."""
        svc_id: str =   _unique_id("svc-reg-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  svc_id in SERVICE_REGISTRY, \
                "Decorated service not found in SERVICE_REGISTRY after registration"

    def test_entry_is_not_registered_in_command_registry(self) -> None:
        """# Assert Decorated Service Does Not Leak into COMMAND_REGISTRY."""
        svc_id: str =   _unique_id("svc-leak-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  svc_id not in COMMAND_REGISTRY, \
                "Decorated service should not appear in COMMAND_REGISTRY"

    def test_registered_entry_is_service_entry(self) -> None:
        """# Assert Registered Entry is a ServiceEntry."""
        svc_id: str =   _unique_id("svc-type-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  isinstance(SERVICE_REGISTRY.get_entry(svc_id), ServiceEntry),   \
                "Registered entry is no longer a ServiceEntry"

    def test_registered_entry_has_correct_config(self) -> None:
        """# Assert Registered Entry Carries the Provided Config Class."""
        svc_id: str =   _unique_id("svc-cfg-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  SERVICE_REGISTRY.get_entry(svc_id).config is ConcreteConfig,   \
                "Registered entry does not carry the provided config class"

    def test_registered_entry_has_correct_service(self) -> None:
        """# Assert Registered Entry Carries the Decorated Service Class."""
        svc_id: str =   _unique_id("svc-cls-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  SERVICE_REGISTRY.get_entry(svc_id).service is _Service,    \
                "Registered entry does not carry the decorated service class"

    def test_registered_entry_has_correct_tags(self) -> None:
        """# Assert Registered Entry Carries the Provided Tags."""
        svc_id: str =   _unique_id("svc-tags-test")

        @register_service(id = svc_id, config = ConcreteConfig, tags = ["market-data", "trading"])
        class _Service(): pass

        assert  SERVICE_REGISTRY.get_entry(svc_id).tags == ["market-data", "trading"], \
                "Registered entry does not carry the provided tags"

    def test_tags_empty_by_default(self) -> None:
        """# Assert Registered Entry Tags are Empty When Not Provided."""
        svc_id: str =   _unique_id("svc-notags-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  SERVICE_REGISTRY.get_entry(svc_id).tags == [], \
                "Registered entry tags should be empty list by default"

    def test_registered_service_filterable_by_tag(self) -> None:
        """# Assert Registered Service is Listed When Filtering by Its Tag."""
        svc_id: str =   _unique_id("svc-filter-test")
        tag:    str =   _unique_id("tag")

        @register_service(id = svc_id, config = ConcreteConfig, tags = [tag])
        class _Service(): pass

        assert  SERVICE_REGISTRY.list_entries(filter_by = [tag]) == [svc_id],   \
                "Registered service not listed when filtering by its tag"

    def test_duplicate_registration_raises(self) -> None:
        """# Assert Registering a Duplicate Service ID Raises DuplicateEntryError."""
        svc_id: str =   _unique_id("svc-dup-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _First(): pass

        with raises(DuplicateEntryError):
            @register_service(id = svc_id, config = ConcreteConfig)
            class _Second(): pass

# SERVICE REGISTRY LOAD SERVICE ====================================================================

class TestServiceRegistryLoadService():
    """# Verify SERVICE_REGISTRY Service Loading."""

    def test_returns_instance_of_registered_service(self) -> None:
        """# Assert load_service() Returns an Instance of the Registered Service Class."""
        svc_id: str =   _unique_id("svc-load-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  isinstance(SERVICE_REGISTRY.load_service(svc_id), _Service),    \
                "load_service() did not return an instance of the registered service class"

    def test_returns_new_instance_per_call(self) -> None:
        """# Assert load_service() Instantiates a New Service on Each Call."""
        svc_id: str =   _unique_id("svc-new-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service(): pass

        assert  SERVICE_REGISTRY.load_service(svc_id) is not SERVICE_REGISTRY.load_service(svc_id), \
                "load_service() should instantiate a new service on each call"

    def test_forwards_arguments_to_service(self) -> None:
        """# Assert load_service() Forwards Positional & Keyword Arguments to Service."""
        svc_id: str =   _unique_id("svc-args-test")

        @register_service(id = svc_id, config = ConcreteConfig)
        class _Service():
            def __init__(self, region: str, trading: bool = False):
                self.region:    str =   region
                self.trading:   bool =  trading

        service =   SERVICE_REGISTRY.load_service(svc_id, "us", trading = True)
        assert  service.region == "us",     \
                "Positional argument not forwarded to service"
        assert  service.trading is True,    \
                "Keyword argument not forwarded to service"

    def test_raises_for_missing_service(self) -> None:
        """# Assert load_service() Raises for an Unregistered Service."""
        with raises(EntryNotFoundError):
            SERVICE_REGISTRY.load_service("ghost-service")