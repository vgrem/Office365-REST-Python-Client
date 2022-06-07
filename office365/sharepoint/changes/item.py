from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.changes.change import Change
from office365.sharepoint.sharing.shared_with_user import SharedWithUser


class ChangeItem(Change):
    """A change on an item."""

    @property
    def shared_with_users(self):
        return self.properties.get("SharedWithUsers", ClientValueCollection(SharedWithUser))
