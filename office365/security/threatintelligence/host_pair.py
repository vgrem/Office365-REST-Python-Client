from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.threatintelligence.host import Host


class HostPair(Entity):
    @property
    def first_seen_date_time(self) -> datetime:
        """Gets the firstSeenDateTime property"""
        return self.properties.get("firstSeenDateTime", datetime.min)

    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def link_kind(self) -> Optional[str]:
        """Gets the linkKind property"""
        return self.properties.get("linkKind", None)

    @property
    def child_host(self) -> Host:
        """Gets the childHost property"""
        return self.properties.get("childHost", Host(self.context, ResourcePath("childHost", self.resource_path)))

    @property
    def parent_host(self) -> Host:
        """Gets the parentHost property"""
        return self.properties.get("parentHost", Host(self.context, ResourcePath("parentHost", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.HostPair"
