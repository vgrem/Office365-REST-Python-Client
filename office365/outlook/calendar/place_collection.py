from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity_collection import EntityCollection
from office365.outlook.calendar.place import Place
from office365.outlook.calendar.rooms.list import RoomList
from office365.outlook.calendar.rooms.room import Room
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.graph_client import GraphClient


class PlaceCollection(EntityCollection[Place]):
    """Tenant places — the ``/places`` endpoint.

    ``/places`` is an abstract collection: it only lists places *by type*, so use
    :attr:`rooms` (``/places/microsoft.graph.room``) or :attr:`room_lists`
    (``/places/microsoft.graph.roomList``) rather than the collection directly.
    """

    def __init__(self, context: "GraphClient", resource_path: Optional[ResourcePath] = None) -> None:
        super().__init__(context, Place, resource_path or ResourcePath("places"))

    @property
    def rooms(self) -> EntityCollection[Room]:
        """All rooms in the tenant (invite one by its ``email_address``)."""
        return EntityCollection(self.context, Room, ResourcePath("microsoft.graph.room", self.resource_path))

    @property
    def room_lists(self) -> EntityCollection[RoomList]:
        """All room lists in the tenant."""
        return EntityCollection(self.context, RoomList, ResourcePath("microsoft.graph.roomList", self.resource_path))
