"""# vectra.services.core.protocol

Abstract service protocol.
"""

__all__ = ["Service"]

from abc                import ABC
from logging            import Logger

from vectra.utilities   import get_logger

class Service(ABC):
    """# Abstract Broker Service"""

    def __init__(self,
        id: str
    ):
        # Define properties.
        self._id_:  str =   id

        # Initialize logger.
        self.__logger__:    Logger =    get_logger(f"{id}-service")

    # PROPERTIES ===================================================================================

    @property
    def id(self) -> str:
        """# Service Identifier"""
        return self._id_

    # METHODS ======================================================================================

    def close(self) -> None:
        """# Release Service Resources.
        
        Override to close connections, streams, sessions, etc. No-op by default.
        """
        pass

    # DUNDERS ======================================================================================

    def __enter__(self) -> "Service":
        """# Instantiate Service in Context."""
        return self

    def __exit__(self, *args) -> None:
        """# Exit Context."""
        self.close()

    def __repr__(self) -> str:
        """# Service Object Representation."""
        return f"""<Service(id = {self.id})>"""