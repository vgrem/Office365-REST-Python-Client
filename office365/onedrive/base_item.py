from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path_entity import ResourcePathEntity


class BaseItem(ClientObject):
    """The baseItem resource is an abstract resource that contains a common set of properties shared among several
    other resources types """

    @property
    def entity_type_name(self):
        return "microsoft.graph." + type(self).__name__

    @property
    def id(self):
        """The unique identifier of the drive."""
        if self.is_property_available("id"):
            return self.properties['id']
        return None

    @property
    def created_by(self):
        """Identity of the user, device, or application which created the item."""
        if self.is_property_available("createdBy"):
            return self.properties['createdBy']
        return None

    @property
    def last_modified_by(self):
        """Identity of the user, device, and application which last modified the item."""
        if self.is_property_available("lastModifiedBy"):
            return self.properties['lastModifiedBy']
        return None

    @property
    def created_datetime(self):
        """Date and time of item creation."""
        if self.is_property_available("createdDateTime"):
            return self.properties['createdDateTime']
        return None

    @property
    def last_modified_datetime(self):
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
    def web_url(self):
        """URL that displays the resource in the browser."""
        if self.is_property_available("webUrl"):
            return self.properties['webUrl']
        return None

    @property
    def resource_path(self):
        resource_path = super(BaseItem, self).resource_path
        if resource_path:
            return resource_path
        if self.is_property_available("Id"):
            return ResourcePathEntity(
                self.context,
                self._parent_collection.resource_path,
                self.properties["Id"])
