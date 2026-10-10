from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class Subscription(Entity):
    @property
    def hash(self) -> Optional[str]:
        """Gets the Hash property"""
        return self.properties.get("Hash", None)

    @property
    def entity_type_name(self) -> str:
        return "SP.BusinessData.Runtime.Subscription"
