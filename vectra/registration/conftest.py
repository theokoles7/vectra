"""# vectra.registration.conftest

Registry fixtures shares across registration tests.
"""

from pytest             import fixture

from vectra.conftest    import ConcreteRegistry


@fixture
def registry() -> ConcreteRegistry:
    """# Fresh, Empty Registry"""
    return ConcreteRegistry()


@fixture
def populated_registry(
    registry:   ConcreteRegistry
) -> ConcreteRegistry:
    """# Registry with Pre-Populated Entries"""
    # Populate registry entries.
    registry.register(entry_id =    "alpha",    tags = ["fast", "stable"])
    registry.register(entry_id =    "beta",     tags = ["fast"])
    registry.register(entry_id =    "gamma",    tags = ["stable"])

    # Provide registry.
    return registry