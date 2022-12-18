from office365.directory.audit.provisioning.service_principal import ProvisioningServicePrincipal
from office365.entity import Entity


class ProvisioningObjectSummary(Entity):
    """Represents an action performed by the Azure AD Provisioning service and its associated properties."""

    @property
    def service_principal(self):
        """Represents the service principal used for provisioning."""
        return self.properties.get("servicePrincipal", ProvisioningServicePrincipal())


