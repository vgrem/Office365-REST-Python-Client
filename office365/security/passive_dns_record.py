from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.artifact import Artifact

if TYPE_CHECKING:
    from office365.security.threatintelligence.host import Host


class PassiveDnsRecord(Entity):
    @property
    def collected_date_time(self) -> datetime:
        """Gets the collectedDateTime property"""
        return self.properties.get("collectedDateTime", datetime.min)

    @property
    def first_seen_date_time(self) -> datetime:
        """Gets the firstSeenDateTime property"""
        return self.properties.get("firstSeenDateTime", datetime.min)

    @property
    def last_seen_date_time(self) -> datetime:
        """Gets the lastSeenDateTime property"""
        return self.properties.get("lastSeenDateTime", datetime.min)

    @property
    def record_type(self) -> Optional[str]:
        """Gets the recordType property"""
        return self.properties.get("recordType", None)

    @property
    def artifact(self) -> Artifact:
        """Gets the artifact property"""
        return self.properties.get("artifact", Artifact(self.context, ResourcePath("artifact", self.resource_path)))

    @property
    def parent_host(self) -> Host:
        """Gets the parentHost property"""
        return self.properties.get("parentHost", Host(self.context, ResourcePath("parentHost", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.PassiveDnsRecord"
