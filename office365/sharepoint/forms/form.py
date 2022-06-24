from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class Form(BaseEntity):
    """A form provides a display and editing interface for a single list item."""

    @property
    def form_type(self):
        """
        Gets the type of the form.

        :rtype: str or None
        """
        return self.properties.get("FormType", None)

    @property
    def server_relative_url(self):
        """
        Gets the server-relative URL of the form.

        :rtype: str or None
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def resource_path(self):
        """
        Gets the Web site–relative Path of the form
        """
        return self.properties.get("ResourcePath", SPResPath())
