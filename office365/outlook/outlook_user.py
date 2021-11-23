from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.outlook_category import OutlookCategory
from office365.runtime.paths.resource_path import ResourcePath


class OutlookUser(Entity):
    """Represents the Outlook services available to a user."""

    def master_categories(self):
        return self.properties.get('masterCategories',
                                   EntityCollection(self.context, OutlookCategory,
                                                    ResourcePath("masterCategories", self.resource_path)))

