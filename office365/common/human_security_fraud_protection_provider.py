from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class HumanSecurityFraudProtectionProvider(Entity):
    @property
    def app_id(self) -> Optional[str]:
        """Gets the appId property"""
        return self.properties.get("appId", None)

    @property
    def server_token(self) -> Optional[str]:
        """Gets the serverToken property"""
        return self.properties.get("serverToken", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.HumanSecurityFraudProtectionProvider"
