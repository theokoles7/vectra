"""# vectra.registration.core.conftest

Entry fixtures for `registration.core` tests
"""

from pytest             import fixture

from vectra.conftest    import ConcreteConfig, ConcreteEntry


@fixture
def entry_no_config() -> ConcreteEntry:
    """# Entry with No Config & No Entry Point"""
    return ConcreteEntry(id = "bare-entry")


@fixture
def entry_with_config() -> ConcreteEntry:
    """# Entry that Carries a Config, no Entry Point"""
    return ConcreteEntry(id = "cfg-entry", config = ConcreteConfig)


@fixture
def entry_with_entry_point() -> ConcreteEntry:
    """# Entry that Carries Entry Point, no Config"""
    # Define an entry point function.
    def ep(*args, **kwargs) -> str: return "result"

    # Create entry.
    return ConcreteEntry(id = "ep-entry", entry_point = ep)


@fixture
def full_entry() -> ConcreteEntry:
    """# Entry with Config, Entry Point, & Two Tags"""
    # Define an entry point function.
    def ep(*args, **kwargs) -> str: return "result"

    # Create entry.
    return  ConcreteEntry(
                id =            "full-entry",
                config =        ConcreteConfig,
                entry_point =   ep,
                tags =          ["a", "b"]
            )