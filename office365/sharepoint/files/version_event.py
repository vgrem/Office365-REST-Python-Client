from office365.sharepoint.base_entity import BaseEntity


class FileVersionEvent(BaseEntity):
    """Represents an event object happened on a Microsoft.SharePoint.SPFile."""

    @property
    def editor(self):
        """Returns the name of the user who initiated the event.

        :rtype: str or None
        """
        return self.properties.get("Editor", None)
