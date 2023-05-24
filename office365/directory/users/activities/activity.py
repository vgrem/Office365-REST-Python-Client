from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class UserActivity(Entity):
    """"""

    @property
    def history_items(self):
        """NavigationProperty/Containment; navigation property to the associated activity."""
        from office365.directory.users.activities.history_item import ActivityHistoryItem
        return self.properties.get('historyItems',
                                   EntityCollection(self.context, ActivityHistoryItem,
                                                    ResourcePath("historyItems", self.resource_path)))
