from __future__ import annotations

from typing import TYPE_CHECKING

from office365.communications.virtualevents.townhall import VirtualEventTownhall
from office365.communications.virtualevents.webinar import VirtualEventWebinar
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.virtualevents.virtual_event import VirtualEvent


class VirtualEventsRoot(Entity):
    """The container for virtual event APIs."""

    @property
    def townhalls(self) -> EntityCollection[VirtualEventTownhall]:
        """A collection of town halls. Nullable."""
        return self.properties.get(
            "townhalls",
            EntityCollection(
                self.context,
                VirtualEventTownhall,
                ResourcePath("townhalls", self.resource_path),
            ),
        )

    @property
    def webinars(self) -> EntityCollection[VirtualEventWebinar]:
        """A collection of webinars. Nullable."""
        return self.properties.get(
            "webinars",
            EntityCollection(
                self.context,
                VirtualEventWebinar,
                ResourcePath("webinars", self.resource_path),
            ),
        )

    @property
    def events(self) -> EntityCollection[VirtualEvent]:
        """Gets the events property"""
        from office365.communications.virtualevents.virtual_event import VirtualEvent

        return self.properties.get(
            "events",
            EntityCollection[VirtualEvent](self.context, VirtualEvent, ResourcePath("events", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventsRoot"
