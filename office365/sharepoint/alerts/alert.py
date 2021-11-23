from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class Alert(BaseEntity):

    @property
    def user(self):
        """Gets user object that represents User for the alert."""
        from office365.sharepoint.principal.user import User
        return self.properties.get('User',
                                   User(self.context, ResourcePath("user", self.resource_path)))

    @property
    def list(self):
        """Gets list object that represents List for the alert."""
        from office365.sharepoint.lists.list import List
        return self.properties.get('List',
                                   List(self.context, ResourcePath("list", self.resource_path)))
