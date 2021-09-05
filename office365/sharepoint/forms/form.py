from office365.sharepoint.base_entity import BaseEntity


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
