from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.sharing.shared_with_user import SharedWithUser


class FileVersionEvent(Entity):
    """Represents an event object happened on a Microsoft.SharePoint.SPFile."""

    @property
    def event_type(self) -> Optional[str]:
        """Returns the type of the event."""
        return self.properties.get("EventType", None)

    @property
    def editor(self) -> Optional[str]:
        """Returns the name of the user who initiated the event."""
        return self.properties.get("Editor", None)

    @odata(name="SharedByUser")
    @property
    def shared_by_user(self) -> SharedWithUser:
        """Returns the shared by user Information in sharing action for change log."""
        return self.properties.get("SharedByUser", SharedWithUser())

    @odata(name="SharedWithUsers")
    @property
    def shared_with_users(self) -> ClientValueCollection[SharedWithUser]:
        """Returns the array of users that have been shared in sharing action for the change log."""
        return self.properties.get("SharedWithUsers", ClientValueCollection(SharedWithUser))

    @property
    def editor_email(self) -> Optional[str]:
        """Gets the EditorEmail property"""
        return self.properties.get("EditorEmail", None)

    @property
    def time(self) -> Optional[datetime]:
        """Gets the Time property"""
        return self.properties.get("Time", datetime.min)
