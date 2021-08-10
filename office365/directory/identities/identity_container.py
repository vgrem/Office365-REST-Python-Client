from office365.directory.identities.b2x_identity_user_flow import B2XIdentityUserFlow
from office365.directory.identities.identity_provider_base import IdentityProviderBase
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.resource_path import ResourcePath


class IdentityContainer(Entity):

    @property
    def identity_providers(self):
        return self.properties.get('identityProviders',
                                   EntityCollection(self.context, IdentityProviderBase,
                                                    ResourcePath("identityProviders", self.resource_path)))

    @property
    def b2x_user_flows(self):
        return self.properties.get('b2xUserFlows',
                                   EntityCollection(self.context, B2XIdentityUserFlow,
                                                    ResourcePath("b2xUserFlows", self.resource_path)))
