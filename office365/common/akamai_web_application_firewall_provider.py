from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AkamaiWebApplicationFirewallProvider(Entity):
    @property
    def access_token(self) -> Optional[str]:
        """Gets the accessToken property"""
        return self.properties.get("accessToken", None)

    @property
    def client_secret(self) -> Optional[str]:
        """Gets the clientSecret property"""
        return self.properties.get("clientSecret", None)

    @property
    def client_token(self) -> Optional[str]:
        """Gets the clientToken property"""
        return self.properties.get("clientToken", None)

    @property
    def host_prefix(self) -> Optional[str]:
        """Gets the hostPrefix property"""
        return self.properties.get("hostPrefix", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AkamaiWebApplicationFirewallProvider"
