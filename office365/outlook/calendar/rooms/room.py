from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.outlook.calendar.place import Place
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.booking.type import BookingType
    from office365.outlook.place_feature_enablement import PlaceFeatureEnablement


class Room(Place):
    """
    Represents a room in a tenant.
    In Exchange Online, each room is associated with a room mailbox. Derived from place.
    """

    @odata(name="audioDeviceName")
    @property
    def audio_device_name(self) -> Optional[str]:
        """Specifies the name of the audio device in the room."""
        return self.properties.get("audioDeviceName", None)

    @odata(name="building")
    @property
    def building(self) -> Optional[str]:
        """Specifies the building name or building number that the room is in."""
        return self.properties.get("building", None)

    @odata(name="bookingType")
    @property
    def booking_type(self) -> BookingType:
        """Gets the bookingType property"""
        from office365.booking.type import BookingType

        return self.properties.get("bookingType", BookingType.unknown)

    @odata(name="capacity")
    @property
    def capacity(self) -> Optional[int]:
        """Gets the capacity property"""
        return self.properties.get("capacity", None)

    @odata(name="displayDeviceName")
    @property
    def display_device_name(self) -> Optional[str]:
        """Gets the displayDeviceName property"""
        return self.properties.get("displayDeviceName", None)

    @odata(name="emailAddress")
    @property
    def email_address(self) -> Optional[str]:
        """Gets the emailAddress property"""
        return self.properties.get("emailAddress", None)

    @odata(name="floorLabel")
    @property
    def floor_label(self) -> Optional[str]:
        """Gets the floorLabel property"""
        return self.properties.get("floorLabel", None)

    @odata(name="floorNumber")
    @property
    def floor_number(self) -> Optional[int]:
        """Gets the floorNumber property"""
        return self.properties.get("floorNumber", None)

    @odata(name="nickname")
    @property
    def nickname(self) -> Optional[str]:
        """Gets the nickname property"""
        return self.properties.get("nickname", None)

    @odata(name="teamsEnabledState")
    @property
    def teams_enabled_state(self) -> PlaceFeatureEnablement:
        """Gets the teamsEnabledState property"""
        from office365.outlook.place_feature_enablement import PlaceFeatureEnablement

        return self.properties.get("teamsEnabledState", PlaceFeatureEnablement.unknown)

    @odata(name="videoDeviceName")
    @property
    def video_device_name(self) -> Optional[str]:
        """Gets the videoDeviceName property"""
        return self.properties.get("videoDeviceName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Room"
