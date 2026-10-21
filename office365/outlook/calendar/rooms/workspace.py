from __future__ import annotations

from typing import Optional

from office365.booking.place_mode import PlaceMode
from office365.outlook.calendar.place import Place
from office365.runtime.types.odata_property import odata


class Workspace(Place):
    """Represents a workspace in a tenant. Derived from place."""

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

    @odata(name="mode")
    @property
    def mode(self) -> PlaceMode:
        """Gets the mode property"""
        return self.properties.get("mode", PlaceMode())

    @odata(name="nickname")
    @property
    def nickname(self) -> Optional[str]:
        """Gets the nickname property"""
        return self.properties.get("nickname", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Workspace"
