from office365.sharepoint.base_entity import BaseEntity


class WebTemplate(BaseEntity):
    """Specifies a site definition or a site template that is used to instantiate a site."""

    def __repr__(self):
        return self.name

    @property
    def description(self):
        """Gets a value that specifies the description of the list template.
        :rtype: str or None
        """
        return self.properties.get('Description', None)

    @property
    def display_category(self):
        """
        Specifies the display name for the category that this site definition configuration or site template is
        a part of.
        :rtype: str or None
        """
        return self.properties.get('DisplayCategory', None)

    @property
    def image_url(self):
        """
        Specifies the URL for the image that is associated with the site definition configuration or site template.
        :rtype: str or None
        """
        return self.properties.get('ImageUrl', None)

    @property
    def is_hidden(self):
        """
        Specifies whether the site definition configuration is displayed in the user interface for creating new sites
        :rtype: bool or None
        """
        return self.properties.get('IsHidden', None)

    @property
    def is_root_web_only(self):
        """
        Specifies whether the site definition configuration or site template can only be applied to the top-level site
        in the site collection.
        :rtype: bool or None
        """
        return self.properties.get('IsRootWebOnly', None)

    @property
    def is_sub_web_only(self):
        """
        Specifies whether the site definition configuration or site template can only be applied to subsites
        created within the site collection.
        :rtype: bool or None
        """
        return self.properties.get('IsSubWebOnly', None)

    @property
    def lcid(self):
        """
        Specifies the LCID for the site definition configuration or site template.
        :rtype: int or None
        """
        return self.properties.get('Lcid', None)

    @property
    def name(self):
        """Gets a value that specifies the display name of the list template.
        :rtype: str or None
        """
        return self.properties.get('Name', None)

    @property
    def title(self):
        """Specifies the display name for the site definition configuration or site template.
        :rtype: str or None
        """
        return self.properties.get('Title', None)
