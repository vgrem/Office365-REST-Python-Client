from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.security.artifact import Artifact
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.security.indicator_source import IndicatorSource


class Indicator(Entity):
    @property
    def artifact(self) -> Artifact:
        """Gets the artifact property"""
        return self.properties.get("artifact", Artifact(self.context, ResourcePath("artifact", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Indicator"

    @property
    def source(self) -> IndicatorSource:
        """Gets the source property"""
        from office365.directory.security.indicator_source import IndicatorSource

        return self.properties.get("source", IndicatorSource.microsoft)
