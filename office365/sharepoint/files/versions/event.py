from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.shared_with_user import SharedWithUser


class FileVersionEvent(BaseEntity):
    """Represents an event object happened on a Microsoft.SharePoint.SPFile."""

    @property
    def event_type(self):
        """Returns the type of the event."""
        return self.properties.get("EventType", None)

    @property
    def editor(self):
        """Returns the name of the user who initiated the event.

        :rtype: str or None
        """
        return self.properties.get("Editor", None)

    @property
    def shared_by_user(self):
        """Returns the shared by user Information in sharing action for change log."""
        return self.properties.get("SharedByUser", SharedWithUser())

    @property
    def shared_with_users(self):
        """Returns the array of users that have been shared in sharing action for the change log."""
        return self.properties.get("SharedWithUsers", ClientValueCollection(SharedWithUser))
