from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class TemporaryAccessPassAuthenticationMethod(Entity):
    @property
    def is_usable(self) -> Optional[bool]:
        """Gets the isUsable property"""
        return self.properties.get("isUsable", None)

    @property
    def is_usable_once(self) -> Optional[bool]:
        """Gets the isUsableOnce property"""
        return self.properties.get("isUsableOnce", None)

    @property
    def lifetime_in_minutes(self) -> Optional[int]:
        """Gets the lifetimeInMinutes property"""
        return self.properties.get("lifetimeInMinutes", None)

    @property
    def method_usability_reason(self) -> Optional[str]:
        """Gets the methodUsabilityReason property"""
        return self.properties.get("methodUsabilityReason", None)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def temporary_access_pass(self) -> Optional[str]:
        """Gets the temporaryAccessPass property"""
        return self.properties.get("temporaryAccessPass", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TemporaryAccessPassAuthenticationMethod"
