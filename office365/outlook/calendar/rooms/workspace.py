from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.outlook.calendar.place import Place

if TYPE_CHECKING:
    from office365.booking.place_mode import PlaceMode


class Workspace(Place):
    """Represents a workspace in a tenant. Derived from place."""

    @property
    def capacity(self) -> Optional[int]:
        """Gets the capacity property"""
        return self.properties.get("capacity", None)

    @property
    def display_device_name(self) -> Optional[str]:
        """Gets the displayDeviceName property"""
        return self.properties.get("displayDeviceName", None)

    @property
    def email_address(self) -> Optional[str]:
        """Gets the emailAddress property"""
        return self.properties.get("emailAddress", None)

    @property
    def mode(self) -> PlaceMode:
        """Gets the mode property"""
        from office365.booking.place_mode import PlaceMode

        return self.properties.get("mode", PlaceMode())

    @property
    def nickname(self) -> Optional[str]:
        """Gets the nickname property"""
        return self.properties.get("nickname", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Workspace"
