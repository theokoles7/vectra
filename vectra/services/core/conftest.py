"""# vectra.services.core.conftest

Service fixtures for `services.core` tests.
"""

from pytest             import fixture

from vectra.conftest    import ClosableService, ConcreteService


@fixture
def service() -> ConcreteService:
    """# Basic ConcreteService Instance"""
    return ConcreteService()


@fixture
def closable_service() -> ClosableService:
    """# Service that Records Calls to close()"""
    return ClosableService()