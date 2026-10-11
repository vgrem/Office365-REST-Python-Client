from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.m365_capability_inbound_access import (
        M365CapabilityInboundAccess,
    )


class M365CapabilityBase(Entity):
    @property
    def inbound_access(self) -> Optional[M365CapabilityInboundAccess]:
        """Gets the inboundAccess property"""
        return self.properties.get("inboundAccess", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.M365CapabilityBase"
