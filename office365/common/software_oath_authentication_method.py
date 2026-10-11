from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class SoftwareOathAuthenticationMethod(Entity):
    @property
    def secret_key(self) -> Optional[str]:
        """Gets the secretKey property"""
        return self.properties.get("secretKey", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SoftwareOathAuthenticationMethod"
