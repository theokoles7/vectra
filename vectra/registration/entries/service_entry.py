"""# vectra.registration.entries.service_entry

Service registration entry.
"""

__all__ = ["ServiceEntry"]

from typing                     import List, Optional, Type

from vectra.configuration       import ServiceConfig
from vectra.registration.core   import Entry
from vectra.services            import Service

class ServiceEntry(Entry):
    """# Service Registration Entry"""

    def __init__(self,
        id:             str,
        config:         Type[ServiceConfig],
        service:        Type[Service],
        tags:           Optional[List[str]] =   None
    ):
        """# Instantiate Service Registration Entry.

        ## Args:
            * id        (str):                  Name of broker service.
            * config    (Type[ServiceConfig]):  Broker service configuration & argument handler.
            * service   (Type[Service]):        Broker service class.
            * tags      (List[str] | None):     Taxonomical descriptors.
        """
        # Initialize entry.
        super(ServiceEntry, self).__init__(id = id, config = config, tags = tags)

        # Define properties.
        self._service_: Type[Service] = service

    # PROPERTIES ===================================================================================

    @property
    def service(self) -> Type[Service]:
        """# Broker Service Class"""
        return self._service_