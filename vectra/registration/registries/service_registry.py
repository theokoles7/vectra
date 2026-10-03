"""# vectra.registration.registries.service_registry

Service registry system.
"""

__all__ = ["ServiceRegistry"]

from typing                         import override

from vectra.registration.core       import Registry
from vectra.registration.entries    import ServiceEntry

class ServiceRegistry(Registry[ServiceEntry]):
    """# Service Registration System"""

    def __init__(self):
        """# Instantiate Service Registration System."""
        super(ServiceRegistry, self).__init__(id = "services")

    # HELPERS ======================================================================================

    @override
    def _create_entry_(self, **kwargs) -> ServiceEntry:
        """# Create Service Entry."""
        return ServiceEntry(**kwargs)