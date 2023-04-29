from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.changes.change import Change
from office365.sharepoint.sharing.shared_with_user import SharedWithUser


class ChangeItem(Change):
    """A change on an item."""

    @property
    def shared_by_user(self):
        """Return the sharedBy User Information in sharing action for change log."""
        return self.properties.get("SharedByUser", SharedWithUser())

    @property
    def shared_with_users(self):
        """Returns the array of users that have been shared in sharing action for the change log."""
        return self.properties.get("SharedWithUsers", ClientValueCollection(SharedWithUser))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "SharedByUser": self.shared_by_user,
                "SharedWithUsers": self.shared_with_users
            }
            default_value = property_mapping.get(name, None)
        return super(ChangeItem, self).get_property(name, default_value)
