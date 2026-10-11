from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class CloudFlareWebApplicationFirewallProvider(Entity):
    @property
    def api_token(self) -> Optional[str]:
        """Gets the apiToken property"""
        return self.properties.get("apiToken", None)

    @property
    def zone_id(self) -> Optional[str]:
        """Gets the zoneId property"""
        return self.properties.get("zoneId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudFlareWebApplicationFirewallProvider"
