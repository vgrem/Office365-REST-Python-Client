from office365.runtime.client_object import ClientObject


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
