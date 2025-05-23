from typing import Optional

from office365.entity import Entity


class SecureScoreControlProfile(Entity):
    """Represents a tenant's secure score per control data. By default, it returns all controls
    for a tenant and can explicitly pull individual controls."""

    @property
    def action_type(self):
        # type: () -> Optional[str]
        """Control action type (Config, Review, Behavior)."""
        return self.properties.get("actionType", None)

    @property
    def action_url(self):
        # type: () -> Optional[str]
        """URL to where the control can be actioned."""
        return self.properties.get("actionUrl", None)

    @property
    def azure_tenant_id(self):
        # type: () -> Optional[str]
        """GUID string for tenant ID."""
        return self.properties.get("azureTenantId", None)
