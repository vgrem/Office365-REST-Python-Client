from office365.directory.identitySet import IdentitySet
from office365.entity import Entity
from office365.onedrive.itemReference import ItemReference


class BaseItem(Entity):
    """The baseItem resource is an abstract resource that contains a common set of properties shared among several
    other resources types """

    @property
    def etag(self):
        """ETag for the item."""
        return self.properties.get('eTag', None)

    @property
    def createdBy(self):
        """Identity of the user, device, or application which created the item."""
        return self.properties.get('createdBy', IdentitySet())

    @property
    def lastModifiedBy(self):
        """Identity of the user, device, and application which last modified the item."""
        return self.properties.get('lastModifiedBy', IdentitySet())

    @property
    def createdDateTime(self):
        """Date and time of item creation."""
        return self.properties.get('createdDateTime', None)

    @property
    def lastModifiedDateTime(self):
        """Date and time the item was last modified."""
        return self.properties.get('lastModifiedDateTime', None)

    @property
    def name(self):
        """The name of the item."""
        return self.properties.get('name', None)

    @name.setter
    def name(self, value):
        self.properties['name'] = value

    @property
    def description(self):
        """Provides a user-visible description of the item."""
        return self.properties.get('description', None)

    @description.setter
    def description(self, value):
        self.properties['description'] = value

    @property
    def web_url(self):
        """URL that displays the resource in the browser."""
        return self.properties.get('webUrl', None)

    @property
    def parentReference(self):
        """Parent information, if the item has a parent."""
        return self.properties.get('parentReference', ItemReference())

    @parentReference.setter
    def parentReference(self, value):
        self.properties['parentReference'] = value

    def set_property(self, name, value, persist_changes=True):
        super(BaseItem, self).set_property(name, value, persist_changes)
        return self
