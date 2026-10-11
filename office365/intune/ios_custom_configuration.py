from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class IosCustomConfiguration(Entity):
    @property
    def payload(self) -> Optional[bytes]:
        """Gets the payload property"""
        return self.properties.get("payload", None)

    @property
    def payload_file_name(self) -> Optional[str]:
        """Gets the payloadFileName property"""
        return self.properties.get("payloadFileName", None)

    @property
    def payload_name(self) -> Optional[str]:
        """Gets the payloadName property"""
        return self.properties.get("payloadName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosCustomConfiguration"
