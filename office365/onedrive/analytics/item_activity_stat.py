from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.analytics.item_activity import ItemActivity
from office365.runtime.paths.resource_path import ResourcePath


class ItemActivityStat(Entity):
    """The itemActivityStat resource provides information about activities that took place
    within an interval of time."""

    @property
    def activities(self):
        """Exposes the itemActivities represented in this itemActivityStat resource."""
        return self.properties.get('activities',
                                   EntityCollection(self.context, ItemActivity,
                                                    ResourcePath("activities", self.resource_path)))
