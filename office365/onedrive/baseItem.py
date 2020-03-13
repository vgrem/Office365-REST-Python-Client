from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath


class BaseItem(ClientObject):
    """The baseItem resource is an abstract resource that contains a common set of properties shared among several
    other resources types """

    def delete_object(self):
        """Deletes the item."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def entityTypeName(self):
        return "microsoft.graph." + type(self).__name__

    @property
    def id(self):
        """The unique identifier of the drive."""
        if self.is_property_available("id"):
            return self.properties['id']
        return None

    @property
    def etag(self):
        """ETag for the item."""
        if self.is_property_available("eTag"):
            return self.properties['eTag']
        return None

    @property
    def createdBy(self):
        """Identity of the user, device, or application which created the item."""
        if self.is_property_available("createdBy"):
            return self.properties['createdBy']
        return None

    @property
    def lastModifiedBy(self):
        """Identity of the user, device, and application which last modified the item."""
        if self.is_property_available("lastModifiedBy"):
            return self.properties['lastModifiedBy']
        return None

    @property
    def createdDateTime(self):
        """Date and time of item creation."""
        if self.is_property_available("createdDateTime"):
            return self.properties['createdDateTime']
        return None

    @property
    def lastModifiedDateTime(self):
        """Date and time the item was last modified."""
        if self.is_property_available("lastModifiedDateTime"):
            return self.properties['lastModifiedDateTime']
        return None

    @property
    def name(self):
        """The name of the item."""
        if self.is_property_available("name"):
            return self.properties['name']
        return None

    @name.setter
    def name(self, value):
        self.properties['name'] = value

    @property
    def description(self):
        """Provides a user-visible description of the item."""
        if self.is_property_available("description"):
            return self.properties['description']
        return None

    @description.setter
    def description(self, value):
        self.properties['description'] = value

    @property
    def webUrl(self):
        """URL that displays the resource in the browser."""
        if self.is_property_available("webUrl"):
            return self.properties['webUrl']
        return None

    def set_property(self, name, value, persist_changes=True):
        super(BaseItem, self).set_property(name, value, persist_changes)
        if name == "id" and self._resource_path is None:
            self._resource_path = ResourcePath(
                value,
                self._parent_collection.resourcePath)
