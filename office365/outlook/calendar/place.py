from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.geo_coordinates import OutlookGeoCoordinates
from office365.outlook.mail.physical_address import PhysicalAddress
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.outlook.calendar.check_in_claim import CheckInClaim


class Place(Entity):
    """Represents basic location attributes such as name, physical address, and geographic coordinates.
    This is the base type for richer location types such as room and roomList."""

    @odata(name="displayName")
    @property
    def display_name(self) -> Optional[str]:
        """The name associated with the place."""
        return self.properties.get("displayName", None)

    @odata(name="address")
    @property
    def address(self) -> PhysicalAddress:
        """The street address of the place."""
        return self.properties.get("address", PhysicalAddress())

    @odata(name="phone")
    @property
    def phone(self) -> Optional[str]:
        """The phone number of the place."""
        return self.properties.get("phone", None)

    @odata(name="geoCoordinates")
    @property
    def geo_coordinates(self) -> OutlookGeoCoordinates:
        """Gets the geoCoordinates property"""
        return self.properties.get("geoCoordinates", OutlookGeoCoordinates())

    @odata(name="isWheelChairAccessible")
    @property
    def is_wheel_chair_accessible(self) -> Optional[bool]:
        """Gets the isWheelChairAccessible property"""
        return self.properties.get("isWheelChairAccessible", None)

    @odata(name="label")
    @property
    def label(self) -> Optional[str]:
        """Gets the label property"""
        return self.properties.get("label", None)

    @odata(name="parentId")
    @property
    def parent_id(self) -> Optional[str]:
        """Gets the parentId property"""
        return self.properties.get("parentId", None)

    @odata(name="placeId")
    @property
    def place_id(self) -> Optional[str]:
        """Gets the placeId property"""
        return self.properties.get("placeId", None)

    @odata(name="tags")
    @property
    def tags(self) -> StringCollection:
        """Gets the tags property"""
        return self.properties.get("tags", StringCollection())

    @odata(name="checkIns", navigation=True)
    @property
    def check_ins(self) -> EntityCollection[CheckInClaim]:
        """Gets the checkIns property"""
        from office365.outlook.calendar.check_in_claim import CheckInClaim

        return self.properties.get(
            "checkIns",
            EntityCollection[CheckInClaim](self.context, CheckInClaim, ResourcePath("checkIns", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Place"
