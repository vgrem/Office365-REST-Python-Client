from __future__ import annotations

from typing import Optional

from office365.runtime.paths.v3.static import StaticPath
from office365.sharepoint.entity import Entity


class ConnectionSettings(Entity):
    """The ConnectionSettings contains information about an endpoint (4) that can be used to connect to it."""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = StaticPath("Microsoft.BusinessData.Infrastructure.SecureStore.ConnectionSettings")
        super().__init__(context, resource_path)

    @property
    def authentication_mode(self) -> Optional[str]:
        """The authentication mode used by the endpoint"""
        return self.properties.get("AuthenticationMode", None)

    @property
    def parent_name(self) -> Optional[str]:
        """The unique name used to identify the parent of the endpoint"""
        return self.properties.get("parentName", None)

    @property
    def entity_type_name(self):
        return "Microsoft.BusinessData.Infrastructure.SecureStore.ConnectionSettings"

    @property
    def connection_settings_type(self) -> Optional[int]:
        """Gets the ConnectionSettingsType property"""
        return self.properties.get("ConnectionSettingsType", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)

    @property
    def proxy_sso_application_id(self) -> Optional[str]:
        """Gets the ProxySSOApplicationId property"""
        return self.properties.get("ProxySSOApplicationId", None)

    @property
    def proxy_target(self) -> Optional[str]:
        """Gets the ProxyTarget property"""
        return self.properties.get("ProxyTarget", None)

    @property
    def sso_application_id(self) -> Optional[str]:
        """Gets the SSOApplicationId property"""
        return self.properties.get("SSOApplicationId", None)

    @property
    def sso_provider_impl_id(self) -> Optional[str]:
        """Gets the SSOProviderImplId property"""
        return self.properties.get("SSOProviderImplId", None)

    @property
    def target(self) -> Optional[str]:
        """Gets the Target property"""
        return self.properties.get("Target", None)
