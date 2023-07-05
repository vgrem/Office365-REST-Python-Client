from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.onedrive.listitems.item_reference import ItemReference


class BaseItem(Entity):
    """The baseItem resource is an abstract resource that contains a auth set of properties shared among several
    other resources types """

    @property
    def etag(self):
        """ETag for the item."""
        return self.properties.get('eTag', None)

    @property
    def created_by(self):
        """Identity of the user, device, or application which created the item."""
        return self.properties.get('createdBy', IdentitySet())

    @property
    def last_modified_by(self):
        """Identity of the user, device, and application which last modified the item."""
        return self.properties.get('lastModifiedBy', IdentitySet())

    @property
    def created_datetime(self):
        """Gets date and time of item creation."""
        return self.properties.get('createdDateTime', None)

    @property
    def last_modified_datetime(self):
        """Gets date and time the item was last modified."""
        return self.properties.get('lastModifiedDateTime', None)

    @property
    def name(self):
        """Gets the name of the item."""
        return self.properties.get('name', None)

    @name.setter
    def name(self, value):
        """
        Sets the name of the item.

        :type value: str
        """
        self.set_property('name', value)

    @property
    def description(self):
        """
        Provides a user-visible description of the item.

        :rtype: str or None
        """
        return self.properties.get('description', None)

    @description.setter
    def description(self, value):
        self.set_property('description', value)

    @property
    def web_url(self):
        """
        URL that displays the resource in the browser.

        :rtype: str or None
        """
        return self.properties.get('webUrl', None)

    @property
    def parent_reference(self):
        """Parent information, if the item has a parent."""
        return self.properties.get('parentReference', ItemReference())

    @parent_reference.setter
    def parent_reference(self, value):
        self.set_property('parentReference', value, False)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "createdBy": self.created_by,
                "lastModifiedBy": self.last_modified_by,
                "parentReference": self.parent_reference
            }
            default_value = property_mapping.get(name, None)
        return super(BaseItem, self).get_property(name, default_value)
