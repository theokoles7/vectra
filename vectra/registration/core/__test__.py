"""# vectra.registration.core.test

Tests for Entry, Registry, and all registration exceptions.
"""

from argparse                               import ArgumentParser

from pytest                                 import raises

from vectra.conftest                        import ConcreteConfig, ConcreteEntry, ConcreteRegistry
from vectra.registration.core.exceptions    import *

# EXCEPTIONS =======================================================================================

class TestRegistrationError():
    """# Verify Generic Registration Error Functionality."""

    def test_is_exception(self) -> None:
        """# Assert that RegistrationError is an Exception."""
        assert  issubclass(RegistrationError, Exception),  \
                "RegistrationError should be type Exception"

    def test_can_raise(self) -> None:
        """# Ensure RegistrationError Can Be Raised."""
        with raises(RegistrationError): raise RegistrationError("Test")


class TestDuplicateEntryError():
    """# Verify Duplicate Entry Error Functionality."""

    def test_is_registration_error(self) -> None:
        """# Assert that DuplicateEntryError is a RegistrationError."""
        assert  issubclass(DuplicateEntryError, RegistrationError), \
                "DuplicateEntryError no longer inherits from RegistrationError"

    def test_message_contains_entry_id(self) -> None:
        """# Ensure DuplicateEntryError Message Contains Entry ID."""
        # Initialize error.
        err:    DuplicateEntryError =   DuplicateEntryError(entry_id = "test", registry_id = "reg")

        # Assert that message contains "test".
        assert  "test" in str(err), "Entry ID no longer appears in error message"

    def test_message_contains_registry_id(self) -> None:
        """# Ensure DuplicateEntryError Message Contains Registry ID."""
        # Initialize error.
        err:    DuplicateEntryError =   DuplicateEntryError(entry_id = "test", registry_id = "reg")

        # Assert that message contains "reg".
        assert  "reg" in str(err), "Registry ID no longer appears in error message"

    def test_can_raise(self) -> None:
        """# Ensure DuplicateEntryError Can Be Raised."""
        with raises(DuplicateEntryError):
            raise DuplicateEntryError(entry_id = "test", registry_id = "reg")


class TestEntryNotFoundError():
    """# Verify Entry Not Found Error Functionality."""

    def test_is_registration_error(self) -> None:
        """# Assert that EntryNotFoundError is a RegistrationError."""
        assert  issubclass(EntryNotFoundError, RegistrationError),  \
                "EntryNotFoundError no longer inherits from RegistrationError"

    def test_message_contains_entry_id(self) -> None:
        """# Ensure EntryNotFoundError Message Contains Entry ID."""
        # Initialize error.
        err:    EntryNotFoundError =    EntryNotFoundError(entry_id = "test", registry_id = "reg")

        # Assert that message contains "test".
        assert  "test" in str(err), "Entry ID no longer appears in error message"

    def test_message_contains_registry_id(self) -> None:
        """# Ensure EntryNotFoundError Message Contains Registry ID."""
        # Initialize error.
        err:    EntryNotFoundError =    EntryNotFoundError(entry_id = "test", registry_id = "reg")

        # Assert that message contains "reg".
        assert  "reg" in str(err), "Registry ID no longer appears in error message"

    def test_can_raise(self) -> None:
        """# Ensure EntryNotFoundError Can Be Raised."""
        with raises(EntryNotFoundError):
            raise EntryNotFoundError(entry_id = "test", registry_id = "reg")


class TestEntryPointNotConfiguredError():
    """# Verify Entry Point Not Configured Error Functionality."""

    def test_is_registration_error(self) -> None:
        """# Assert that EntryPointNotConfiguredError is a RegistrationError."""
        assert  issubclass(EntryPointNotConfiguredError, RegistrationError),    \
                "EntryPointNotConfiguredError no longer inherits from RegistrationError"

    def test_message_contains_entry_id(self) -> None:
        """# Ensure EntryPointNotConfiguredError Message Contains Entry ID."""
        # Initialize error.
        err:    EntryPointNotConfiguredError =   EntryPointNotConfiguredError(entry_id = "test")

        # Assert that message contains "test".
        assert  "test" in str(err), "Entry ID no longer appears in error message"

    def test_can_raise(self) -> None:
        """# Ensure EntryPointNotConfiguredError Can Be Raised."""
        with raises(EntryPointNotConfiguredError):
            raise EntryPointNotConfiguredError(entry_id = "test")


class TestParserNotConfiguredError():
    """# Verify Parser Not Configured Error Functionality."""

    def test_is_registration_error(self) -> None:
        """# Assert that ParserNotConfiguredError is a RegistrationError."""
        assert  issubclass(ParserNotConfiguredError, RegistrationError),    \
                "ParserNotConfiguredError no longer inherits from RegistrationError"

    def test_message_contains_entry_id(self) -> None:
        """# Ensure ParserNotConfiguredError Message Contains Entry ID."""
        # Initialize error.
        err:    ParserNotConfiguredError =   ParserNotConfiguredError(entry_id = "test")

        # Assert that message contains "test".
        assert  "test" in str(err), "Entry ID no longer appears in error message"

    def test_can_raise(self) -> None:
        """# Ensure ParserNotConfiguredError Can Be Raised."""
        with raises(ParserNotConfiguredError): raise ParserNotConfiguredError(entry_id = "test")


class TestRegistryNotLoadedError():
    """# Verify Registry Not Loaded Error Functionality."""

    def test_is_registration_error(self) -> None:
        """# Assert that RegistryNotLoadedError is a RegistrationError."""
        assert  issubclass(RegistryNotLoadedError, RegistrationError),  \
                "RegistryNotLoadedError no longer inherits from RegistrationError"

    def test_message_contains_registry_id(self) -> None:
        """# Ensure RegistryNotLoadedError Message Contains Registry ID."""
        # Initialize error.
        err:    RegistryNotLoadedError =    RegistryNotLoadedError(registry_id = "test")
        assert  "test" in str(err), "Registry ID no longer appears in error message"

    def test_can_raise(self) -> None:
        """# Ensure RegistryNotLoadedError Can Be Raised."""
        with raises(RegistryNotLoadedError):
            raise RegistryNotLoadedError(registry_id = "test")


# ENTRY PROPERTIES =================================================================================

class TestEntryProperties():
    """# Verify Entry Properties Are Defined/Accessed Properly."""

    def test_id(self, full_entry: ConcreteEntry) -> None:
        """# Test Entry ID Access."""
        assert  full_entry.id == "full-entry",  \
                "Entry ID inaccessible or incorrect"

    def test_config(self, full_entry: ConcreteEntry) -> None:
        """# Test Entry Config Access."""
        assert  full_entry.config is ConcreteConfig,    \
                "Entry config inaccessible or incorrect"

    def test_config_none_when_absent(self, entry_no_config: ConcreteEntry) -> None:
        """# Assert Entry Config is None When Not Provided."""
        assert  entry_no_config.config is None, \
                "Entry config should be None when not provided"

    def test_entry_point_callable(self, full_entry: ConcreteEntry) -> None:
        """# Assert Entry Point is Callable."""
        assert  callable(full_entry.entry_point),   \
                "Entry point is no longer callable"

    def test_entry_point_none_when_absent(self, entry_no_config: ConcreteEntry) -> None:
        """# Assert Entry Point is None When Not Provided."""
        assert  entry_no_config.entry_point is None,    \
                "Entry point should be None when not provided"

    def test_tags(self, full_entry: ConcreteEntry) -> None:
        """# Test Entry Tags Access."""
        assert  full_entry.tags == ["a", "b"],  \
                "Entry tags inaccessible or incorrect"

    def test_tags_empty_by_default(self) -> None:
        """# Assert Entry Tags are Empty by Default."""
        entry:  ConcreteEntry = ConcreteEntry(id = "tagless")
        assert  entry.tags == [],   \
                "Entry tags should be empty list by default"


# ENTRY HAS TAG ====================================================================================

class TestEntryHasTag():
    """# Verify Entry Tag Querying."""

    def test_present_tag_returns_true(self, full_entry: ConcreteEntry) -> None:
        """# Assert has_tag() Returns True for Present Tag."""
        assert  full_entry.has_tag("a") is True,    \
                "has_tag() should return True for a present tag"

    def test_absent_tag_returns_false(self, full_entry: ConcreteEntry) -> None:
        """# Assert has_tag() Returns False for Absent Tag."""
        assert  full_entry.has_tag("z") is False,   \
                "has_tag() should return False for an absent tag"

    def test_empty_tags_always_false(self, entry_no_config: ConcreteEntry) -> None:
        """# Assert has_tag() Always Returns False When Tags are Empty."""
        assert  entry_no_config.has_tag("anything") is False,  \
                "has_tag() should always return False when tags are empty"


# ENTRY REGISTER CONFIGURATION =====================================================================

class TestEntryRegisterConfiguration():
    """# Verify Entry Configuration Registration."""

    def test_registers_successfully_with_config(self) -> None:
        """# Assert register_configuration() Succeeds When Config is Present."""
        parent:     ArgumentParser =    ArgumentParser(prog = "parent")
        subparsers                =     parent.add_subparsers(dest = "cmd")
        entry:      ConcreteEntry =     ConcreteEntry(id = "cfg-entry", config = ConcreteConfig)
        entry.register_configuration(subparser = subparsers)

    def test_raises_when_no_config(self, entry_no_config: ConcreteEntry) -> None:
        """# Assert register_configuration() Raises When No Config is Present."""
        parent:     ArgumentParser =    ArgumentParser(prog = "parent")
        subparsers                =     parent.add_subparsers(dest = "cmd")
        with raises(ParserNotConfiguredError):
            entry_no_config.register_configuration(subparser = subparsers)


# ENTRY DUNDERS ====================================================================================

class TestEntryDunders():
    """# Verify Entry Dunder Methods."""

    def test_repr_contains_id(self, full_entry: ConcreteEntry) -> None:
        """# Assert Entry __repr__ Contains Entry ID."""
        assert  "full-entry" in repr(full_entry),   \
                "Entry ID no longer appears in __repr__"

    def test_repr_contains_tags(self, full_entry: ConcreteEntry) -> None:
        """# Assert Entry __repr__ Contains Entry Tags."""
        r:  str =   repr(full_entry)
        assert  "a" in r and "b" in r,  \
                "Entry tags no longer appear in __repr__"


# REGISTRY PROPERTIES ==============================================================================

class TestRegistryProperties():
    """# Verify Registry Properties Are Defined/Accessed Properly."""

    def test_id(self, registry: ConcreteRegistry) -> None:
        """# Test Registry ID Access."""
        assert  registry.id == "test", "Registry ID inaccessible or incorrect"

    def test_is_loaded_false_initially(self, registry: ConcreteRegistry) -> None:
        """# Assert Registry is Not Loaded on Initialization."""
        assert  registry.is_loaded is False,    \
                "Registry should not be loaded on initialization"

    def test_entries_empty_initially(self, registry: ConcreteRegistry) -> None:
        """# Assert Registry Entries are Empty on Initialization."""
        assert  registry._entries_ == {},   \
                "Registry entries should be empty on initialization"


# REGISTRY LAZY LOAD ===============================================================================

class TestRegistryLazyLoad():
    """# Verify Registry Lazy-Load Behavior."""

    def test_is_loaded_after_get_entry_attempt(self, registry: ConcreteRegistry) -> None:
        """# Assert Registry is Loaded After get_entry() is Called."""
        with raises(EntryNotFoundError): registry.get_entry("nonexistent")
        assert  registry.is_loaded is True, \
                "Registry should be loaded after get_entry() is called"

    def test_is_loaded_after_list_entries(self, registry: ConcreteRegistry) -> None:
        """# Assert Registry is Loaded After list_entries() is Called."""
        registry.list_entries()
        assert  registry.is_loaded is True, \
                "Registry should be loaded after list_entries() is called"

    def test_is_loaded_after_register_configurations(self, registry: ConcreteRegistry) -> None:
        """# Assert Registry is Loaded After register_configurations() is Called."""
        registry.register_configurations(
            subparser = ArgumentParser().add_subparsers(dest = "cmd")
        )
        assert  registry.is_loaded is True, \
                "Registry should be loaded after register_configurations() is called"


# REGISTRY REGISTER ================================================================================

class TestRegistryRegister():
    """# Verify Registry Entry Registration."""

    def test_register_adds_entry(self, registry: ConcreteRegistry) -> None:
        """# Assert register() Adds Entry to Registry."""
        registry.register(entry_id = "new")
        assert  "new" in registry,  \
                "Entry not found in registry after registration"

    def test_register_duplicate_raises(self, registry: ConcreteRegistry) -> None:
        """# Assert register() Raises for Duplicate Entry."""
        registry.register(entry_id = "dup")
        with raises(DuplicateEntryError):
            registry.register(entry_id = "dup")

    def test_register_passes_kwargs_to_entry(self, registry: ConcreteRegistry) -> None:
        """# Assert register() Passes Keyword Arguments to Entry."""
        def _ep(): return 42
        registry.register(entry_id = "kw", entry_point = _ep, tags = ["x"])
        entry:  ConcreteEntry = registry.get_entry("kw")
        assert  entry.entry_point is _ep,   \
                "Entry point not passed to entry on registration"
        assert  entry.tags == ["x"],        \
                "Tags not passed to entry on registration"

    def test_entries_returns_copy(self, registry: ConcreteRegistry) -> None:
        """# Assert entries Property Returns a Copy of the Internal Dict."""
        registry.register(entry_id = "safe")
        snapshot:               dict =  registry.entries
        snapshot["injected"]    =       object()
        assert  "injected" not in registry, \
                "Mutating entries snapshot should not affect the registry"


# REGISTRY GET ENTRY ===============================================================================

class TestRegistryGetEntry():
    """# Verify Registry Entry Retrieval."""

    def test_returns_correct_entry(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert get_entry() Returns the Correct Entry."""
        entry:  ConcreteEntry = populated_registry.get_entry("alpha")
        assert  entry.id == "alpha",    \
                "get_entry() returned incorrect entry"

    def test_raises_for_missing_entry(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert get_entry() Raises for a Missing Entry."""
        with raises(EntryNotFoundError):
            populated_registry.get_entry("nonexistent")


# REGISTRY DISPATCH ================================================================================

class TestRegistryDispatch():
    """# Verify Registry Entry Point Dispatch."""

    def test_dispatches_and_returns_value(self, registry: ConcreteRegistry) -> None:
        """# Assert dispatch() Calls Entry Point and Returns Its Value."""
        def _ep(*args, **kwargs): return "dispatched"
        registry.register(entry_id = "dispatchable", entry_point = _ep)
        result = registry.dispatch("dispatchable")
        assert  result == "dispatched", \
                "dispatch() did not return the entry point's return value"

    def test_dispatch_forwards_kwargs(self, registry: ConcreteRegistry) -> None:
        """# Assert dispatch() Forwards Keyword Arguments to Entry Point."""
        received:   dict = {}
        def _ep(**kwargs): received.update(kwargs)
        registry.register(entry_id = "kwarg-ep", entry_point = _ep)
        registry.dispatch("kwarg-ep", foo = "bar", baz = 1)
        assert  received["foo"] == "bar",   \
                "Keyword argument 'foo' not forwarded to entry point"
        assert  received["baz"] == 1,       \
                "Keyword argument 'baz' not forwarded to entry point"

    def test_dispatch_raises_when_no_entry_point(self, registry: ConcreteRegistry) -> None:
        """# Assert dispatch() Raises When Entry Has No Entry Point."""
        registry.register(entry_id = "no-ep")
        with raises(EntryPointNotConfiguredError):
            registry.dispatch("no-ep")

    def test_dispatch_raises_for_missing_entry(self, registry: ConcreteRegistry) -> None:
        """# Assert dispatch() Raises for a Missing Entry."""
        with raises(EntryNotFoundError):
            registry.dispatch("ghost")


# REGISTRY LIST ENTRIES ============================================================================

class TestRegistryListEntries():
    """# Verify Registry Entry Listing."""

    def test_returns_all_ids_unfiltered(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert list_entries() Returns All Entry IDs When Unfiltered."""
        ids:    list =  populated_registry.list_entries()
        assert  set(ids) == {"alpha", "beta", "gamma"},     \
                "list_entries() did not return all registered entry IDs"

    def test_filter_single_tag(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert list_entries() Filters Correctly by a Single Tag."""
        ids:    list =  populated_registry.list_entries(filter_by = ["fast"])
        assert  set(ids) == {"alpha", "beta"},  \
                "list_entries() did not filter correctly by single tag"

    def test_filter_multiple_tags_intersection(self,
        populated_registry: ConcreteRegistry
    ) -> None:
        """# Assert list_entries() Filters by Intersection of Multiple Tags."""
        ids:    list =  populated_registry.list_entries(filter_by = ["fast", "stable"])
        assert  set(ids) == {"alpha"},  \
                "list_entries() did not filter correctly by multiple tags"

    def test_filter_no_matches_returns_empty(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert list_entries() Returns Empty List When No Entries Match Filter."""
        ids:    list =  populated_registry.list_entries(filter_by = ["nonexistent"])
        assert  ids == [],  \
                "list_entries() should return empty list when no entries match filter"

    def test_empty_registry_returns_empty(self, registry: ConcreteRegistry) -> None:
        """# Assert list_entries() Returns Empty List for Empty Registry."""
        assert  registry.list_entries() == [], \
                "list_entries() should return empty list for empty registry"


# REGISTRY DUNDERS =================================================================================

class TestRegistryDunders():
    """# Verify Registry Dunder Methods."""

    def test_contains_true_for_registered(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert __contains__ Returns True for a Registered Entry."""
        assert  "alpha" in populated_registry,  \
                "__contains__ should return True for a registered entry"

    def test_contains_false_for_absent(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert __contains__ Returns False for an Absent Entry."""
        assert  "zeta" not in populated_registry,   \
                "__contains__ should return False for an absent entry"

    def test_len_matches_registration_count(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert __len__ Matches the Number of Registered Entries."""
        assert  len(populated_registry) == 3,   \
                "__len__ does not match number of registered entries"

    def test_len_zero_for_empty(self, registry: ConcreteRegistry) -> None:
        """# Assert __len__ is Zero for an Empty Registry."""
        registry.list_entries()
        assert  len(registry) == 0, \
                "__len__ should be zero for an empty registry"

    def test_getitem_returns_entry(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert __getitem__ Returns the Correct Entry."""
        entry:  ConcreteEntry = populated_registry["alpha"]
        assert  entry.id == "alpha",    \
                "__getitem__ returned incorrect entry"

    def test_getitem_raises_for_missing(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert __getitem__ Raises for a Missing Entry."""
        with raises(EntryNotFoundError):
            _ = populated_registry["ghost"]

    def test_repr_contains_id(self, registry: ConcreteRegistry) -> None:
        """# Assert __repr__ Contains Registry ID."""
        assert  "test" in repr(registry),   \
                "Registry ID no longer appears in __repr__"

    def test_repr_contains_size(self, populated_registry: ConcreteRegistry) -> None:
        """# Assert __repr__ Contains Registry Size."""
        assert  "3" in repr(populated_registry),    \
                "Registry size no longer appears in __repr__"


# REGISTRY REGISTER CONFIGURATIONS =================================================================

class TestRegistryRegisterConfigurations():
    """# Verify Registry Configuration Registration."""

    def test_registers_all_entry_configurations(self, registry: ConcreteRegistry) -> None:
        """# Assert register_configurations() Registers All Entry Configurations."""
        registry.register(entry_id = "cmd-a", config = ConcreteConfig)
        parent:     ArgumentParser =    ArgumentParser(prog = "parent")
        subparsers                =     parent.add_subparsers(dest = "command")
        registry.register_configurations(subparser = subparsers)
        ns  =   parent.parse_args(["test-parser"])
        assert  ns.command == "test-parser",    \
                "Entry configuration not registered as sub-command"

    def test_raises_for_entry_without_config(self, registry: ConcreteRegistry) -> None:
        """# Assert register_configurations() Raises for Entry Without Config."""
        registry.register(entry_id = "no-cfg")
        parent:     ArgumentParser =    ArgumentParser(prog = "parent")
        subparsers                =     parent.add_subparsers(dest = "command")
        with raises(ParserNotConfiguredError):
            registry.register_configurations(subparser = subparsers)