from office365.runtime.client_object import ClientObject
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entity import ResourcePathEntity


class Principal(ClientObject):
    """Represents a user or group that can be assigned permissions to control security."""

    @property
    def id(self):
        """Gets a value that specifies the member identifier for the user or group."""
        if self.is_property_available('Id'):
            return self.properties['Id']
        else:
            return None

    @property
    def title(self):
        """Gets a value that specifies the name of the principal."""
        if self.is_property_available('Title'):
            return self.properties['Title']
        else:
            return None

    @title.setter
    def title(self, value):
        self.properties['Title'] = value

    @property
    def login_name(self):
        """Gets the login name of the principal."""
        if self.is_property_available('LoginName'):
            return self.properties['LoginName']
        else:
            return None

    @property
    def is_hidden_in_ui(self):
        """Gets the login name of the principal."""
        if self.is_property_available('IsHiddenInUI'):
            return self.properties['IsHiddenInUI']
        else:
            return None

    @property
    def principal_type(self):
        """Gets the login name of the principal."""
        if self.is_property_available('PrincipalType'):
            return self.properties['PrincipalType']
        else:
            return None

    @property
    def resource_path(self):
        resource_path = super(Principal, self).resource_path
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            self._resource_path = ResourcePathEntity(
                self.context,
                self._parent_collection.resource_path,
                ODataPathParser.from_method("GetById", [self.properties["Id"]]))
        elif self.is_property_available("LoginName"):
            self._resource_path = ResourcePathEntity(
                self.context,
                self._parent_collection.resource_path,
                ODataPathParser.from_method("GetByName", [self.properties["LoginName"]]))
