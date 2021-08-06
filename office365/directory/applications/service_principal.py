from office365.directory.directory_object import DirectoryObject


class ServicePrincipal(DirectoryObject):
    """Represents an instance of an application in a directory."""

    @property
    def app_display_name(self):
        """The collection of key credentials associated with the application. Not nullable.
        """
        return self.properties.get('appDisplayName', None)

    def add_key(self, key_credential, password_credential, proof):
        pass

    def add_password(self):
        pass
