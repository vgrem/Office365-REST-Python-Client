from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.building_map import BuildingMap
    from office365.outlook.place_feature_enablement import PlaceFeatureEnablement
    from office365.outlook.resource_link import ResourceLink


class Building(Entity):
    @property
    def resource_links(self) -> ClientValueCollection[ResourceLink]:
        """Gets the resourceLinks property"""
        from office365.outlook.resource_link import ResourceLink

        return self.properties.get("resourceLinks", ClientValueCollection[ResourceLink](ResourceLink))

    @property
    def wifi_state(self) -> PlaceFeatureEnablement:
        """Gets the wifiState property"""
        from office365.outlook.place_feature_enablement import PlaceFeatureEnablement

        return self.properties.get("wifiState", PlaceFeatureEnablement.unknown)

    @property
    def map(self) -> BuildingMap:
        """Gets the map property"""
        from office365.common.building_map import BuildingMap

        return self.properties.get("map", BuildingMap(self.context, ResourcePath("map", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Building"
