from office365.sharepoint.base_entity import BaseEntity


class WebTemplate(BaseEntity):
    """Specifies a site definition or a site template that is used to instantiate a site."""

    @property
    def name(self):
        """Gets a value that specifies the display name of the list template."""
        return self.properties.get('Name', None)

    @property
    def description(self):
        """Gets a value that specifies the description of the list template."""
        return self.properties.get('Description', None)
