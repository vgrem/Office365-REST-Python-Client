from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.fixture_map import FixtureMap
    from office365.common.section_map import SectionMap
    from office365.common.unit_map import UnitMap


class LevelMap(Entity):
    @property
    def place_id(self) -> Optional[str]:
        """Gets the placeId property"""
        return self.properties.get("placeId", None)

    @property
    def fixtures(self) -> EntityCollection[FixtureMap]:
        """Gets the fixtures property"""
        from office365.common.fixture_map import FixtureMap

        return self.properties.get(
            "fixtures",
            EntityCollection[FixtureMap](self.context, FixtureMap, ResourcePath("fixtures", self.resource_path)),
        )

    @property
    def sections(self) -> EntityCollection[SectionMap]:
        """Gets the sections property"""
        from office365.common.section_map import SectionMap

        return self.properties.get(
            "sections",
            EntityCollection[SectionMap](self.context, SectionMap, ResourcePath("sections", self.resource_path)),
        )

    @property
    def units(self) -> EntityCollection[UnitMap]:
        """Gets the units property"""
        from office365.common.unit_map import UnitMap

        return self.properties.get(
            "units", EntityCollection[UnitMap](self.context, UnitMap, ResourcePath("units", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LevelMap"
