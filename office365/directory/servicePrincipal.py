from office365.directory.directoryObject import DirectoryObject
from office365.entity_collection import EntityCollection


class ServicePrincipal(DirectoryObject):
    """Represents an instance of an application in a directory."""

    @property
    def app_display_name(self):
        """The collection of key credentials associated with the application. Not nullable.
        """
        return self.properties.get('appDisplayName', None)

    def add_key(self, keyCredential, passwordCredential, proof):
        pass

    def add_password(self):
        pass


class ServicePrincipalCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(ServicePrincipalCollection, self).__init__(context, ServicePrincipal, resource_path)

    def add(self, app_id):
        return self.add_from_json({"appId": app_id})
