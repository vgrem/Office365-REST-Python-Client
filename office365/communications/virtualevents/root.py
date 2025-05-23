from office365.communications.virtualevents.townhall import VirtualEventTownhall
from office365.communications.virtualevents.webinar import VirtualEventWebinar
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class VirtualEventsRoot(Entity):
    """The container for virtual event APIs."""

    @property
    def townhalls(self):
        # type: () -> EntityCollection[VirtualEventTownhall]
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
    def webinars(self):
        # type: () -> EntityCollection[VirtualEventWebinar]
        """A collection of webinars. Nullable."""
        return self.properties.get(
            "webinars",
            EntityCollection(
                self.context,
                VirtualEventWebinar,
                ResourcePath("webinars", self.resource_path),
            ),
        )
