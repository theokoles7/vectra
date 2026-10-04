"""# vectra.services.core.test

Tests for the abstract service protocol.
"""

from logging            import Logger

from pytest             import raises

from vectra.conftest    import ClosableService, ConcreteService

# SERVICE PROPERTIES ===============================================================================

class TestServiceProperties():
    """# Verify Service Properties Are Defined/Accessed Properly."""

    def test_id(self, service: ConcreteService) -> None:
        """# Test Service ID Access."""
        assert  service.id == "test",   \
                "Service ID inaccessible or incorrect"

    def test_id_matches_constructor_argument(self) -> None:
        """# Assert Service ID Reflects Value Provided at Instantiation."""
        assert  ConcreteService(id = "webull").id == "webull",  \
                "Service ID does not reflect value provided at instantiation"


# SERVICE LOGGER ===================================================================================

class TestServiceLogger():
    """# Verify Service Logger Initialization."""

    def test_logger_is_logger(self, service: ConcreteService) -> None:
        """# Assert Service Logger is a Logger."""
        assert  isinstance(service.__logger__, Logger), \
                "Service logger is no longer type Logger"

    def test_logger_named_after_service(self, service: ConcreteService) -> None:
        """# Assert Service Logger Name Identifies the Service."""
        assert  service.__logger__.name.endswith("test-service"),   \
                "Service logger name no longer identifies the service"

    def test_logger_is_child_of_package_logger(self, service: ConcreteService) -> None:
        """# Assert Service Logger is a Child of the Package Logger."""
        assert  service.__logger__.name.startswith("vectra."),  \
                "Service logger is no longer a child of the package logger"


# SERVICE CLOSE ====================================================================================

class TestServiceClose():
    """# Verify Default Service Closure Behavior."""

    def test_close_returns_none(self, service: ConcreteService) -> None:
        """# Assert Default close() Returns None."""
        assert  service.close() is None,    \
                "Default close() should return None"

    def test_close_is_repeatable(self, service: ConcreteService) -> None:
        """# Assert Default close() Can Be Called Repeatedly Without Error."""
        service.close()
        service.close()


# SERVICE CONTEXT MANAGER ==========================================================================

class TestServiceContextManager():
    """# Verify Service Context Manager Behavior."""

    def test_enter_returns_service(self, service: ConcreteService) -> None:
        """# Assert Entering Context Yields the Service Itself."""
        with service as entered:
            assert  entered is service, \
                    "Entering context should yield the service itself"

    def test_close_not_called_within_context(self, closable_service: ClosableService) -> None:
        """# Assert close() is Not Called Before Exiting Context."""
        with closable_service:
            assert  closable_service.close_calls == 0,  \
                    "close() should not be called before exiting context"

    def test_close_called_once_on_exit(self, closable_service: ClosableService) -> None:
        """# Assert close() is Called Exactly Once on Exiting Context."""
        with closable_service: pass

        assert  closable_service.close_calls == 1,  \
                "close() should be called exactly once on exiting context"

    def test_close_called_when_context_raises(self, closable_service: ClosableService) -> None:
        """# Assert close() is Called Even When Context Raises."""
        with raises(RuntimeError):
            with closable_service: raise RuntimeError("Test")

        assert  closable_service.close_calls == 1,  \
                "close() should be called even when context raises"

    def test_exception_propagates_from_context(self, closable_service: ClosableService) -> None:
        """# Assert Exceptions Raised Within Context are Not Suppressed."""
        with raises(RuntimeError, match = "propagate"):
            with closable_service: raise RuntimeError("propagate")


# SERVICE DUNDERS ==================================================================================

class TestServiceDunders():
    """# Verify Service Dunder Methods."""

    def test_repr_contains_id(self, service: ConcreteService) -> None:
        """# Assert Service __repr__ Contains Service ID."""
        assert  "test" in repr(service),    \
                "Service ID no longer appears in __repr__"