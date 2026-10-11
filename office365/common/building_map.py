from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.footprint_map import FootprintMap
    from office365.common.level_map import LevelMap


class BuildingMap(Entity):
    @property
    def place_id(self) -> Optional[str]:
        """Gets the placeId property"""
        return self.properties.get("placeId", None)

    @property
    def footprints(self) -> EntityCollection[FootprintMap]:
        """Gets the footprints property"""
        from office365.common.footprint_map import FootprintMap

        return self.properties.get(
            "footprints",
            EntityCollection[FootprintMap](self.context, FootprintMap, ResourcePath("footprints", self.resource_path)),
        )

    @property
    def levels(self) -> EntityCollection[LevelMap]:
        """Gets the levels property"""
        from office365.common.level_map import LevelMap

        return self.properties.get(
            "levels", EntityCollection[LevelMap](self.context, LevelMap, ResourcePath("levels", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BuildingMap"
