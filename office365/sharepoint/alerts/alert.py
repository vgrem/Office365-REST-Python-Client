from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class Alert(BaseEntity):
    """
    Represents an alert, which generates periodic e-mail notifications sent to a user about the list, list item,
    document, or document library to which the alert applies. SP.Alert provides information about the alert,
    such as which alert template is used, the alert frequency, and the UserID of the user who created the alert.

    The AlertTime, ItemID, ListID and ListUrl properties are not included in the default scalar property
    set for this type.
    """

    @property
    def user(self):
        """Gets user object that represents User for the alert."""
        from office365.sharepoint.principal.users.user import User
        return self.properties.get('User',
                                   User(self.context, ResourcePath("user", self.resource_path)))

    @property
    def list(self):
        """Gets list object that represents List for the alert."""
        from office365.sharepoint.lists.list import List
        return self.properties.get('List',
                                   List(self.context, ResourcePath("list", self.resource_path)))
