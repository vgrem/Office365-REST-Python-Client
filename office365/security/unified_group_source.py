from __future__ import annotations

from office365.directory.groups.group import Group
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.healthissues.sourcetype import SourceType


class UnifiedGroupSource(Entity):
    @property
    def included_sources(self) -> SourceType:
        """Gets the includedSources property"""
        return self.properties.get("includedSources", SourceType.mailbox)

    @property
    def group(self) -> Group:
        """Gets the group property"""
        return self.properties.get("group", Group(self.context, ResourcePath("group", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.UnifiedGroupSource"
