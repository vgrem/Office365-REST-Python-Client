from office365.sharepoint.base_entity import BaseEntity


class SitePageMetadata(BaseEntity):
    """Represents the core properties of a Site Page."""

    @property
    def absolute_url(self):
        """Gets the absolute Url of the Site Page.

        :rtype: str or None
        """
        return self.properties.get('AbsoluteUrl', None)

    @property
    def content_type_id(self):
        """Gets the content type ID of the current Site Page.

        :rtype: str or None
        """
        return self.properties.get('ContentTypeId', None)

    @content_type_id.setter
    def content_type_id(self, value):
        """Sets the content type ID of the current Site Page.

        :rtype: str or None
        """
        self.set_property('ContentTypeId', value)
