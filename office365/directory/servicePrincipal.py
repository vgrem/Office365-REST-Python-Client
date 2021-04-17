from office365.entity import Entity
from office365.entity_collection import EntityCollection


class ServicePrincipal(Entity):

    def add_key(self, keyCredential, passwordCredential, proof):
        pass

    def add_password(self):
        pass


class ServicePrincipalCollection(EntityCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(ServicePrincipalCollection, self).__init__(context, ServicePrincipal, resource_path)

    def add(self, app_id):
        return self.add_from_json({"appId": app_id})
