from office365.directory.identityProvider import IdentityProvider
from office365.entity_collection import EntityCollection


class IdentityProviderCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(IdentityProviderCollection, self).__init__(context, IdentityProvider, resource_path)
