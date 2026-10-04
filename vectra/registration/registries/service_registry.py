"""# vectra.registration.registries.service_registry

Service registry system.
"""

__all__ = ["ServiceRegistry"]

from typing                         import override, Type

from vectra.registration.core       import Registry
from vectra.registration.entries    import ServiceEntry

class ServiceRegistry(Registry[ServiceEntry]):
    """# Service Registration System"""

    def __init__(self):
        """# Instantiate Service Registration System."""
        super(ServiceRegistry, self).__init__(id = "services")

    # METHODS ======================================================================================

    def load_service(self,
        service_id: str,
        *args,
        **kwargs
    ) -> Type:
        """# Load & Instantiate Service.

        ## Args:
            * service_id    (str):  Identifier of service being loaded.

        ## Raises:
            * EntryNotFoundError:   If service queried is not registered.

        ## Returns:
            * Service:  Service instantiated with provided arguments.
        """
        # Query for registered service.
        entry:  ServiceEntry =  self.get_entry(entry_id = service_id)

        # Debug loading.
        self.__logger__.debug(f"Loading {service_id}: {kwargs}")

        # Load service.
        return entry.service(*args, **kwargs)

    # HELPERS ======================================================================================

    @override
    def _create_entry_(self, **kwargs) -> ServiceEntry:
        """# Create Service Entry."""
        return ServiceEntry(**kwargs)