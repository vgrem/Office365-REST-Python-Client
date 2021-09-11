from examples import acquire_token_by_client_credentials
from office365.directory.identities.providers.identity_provider_base import IdentityProviderBase
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_client_credentials)
providers = client.identity.identity_providers.get().execute_query()
for idp in providers:  # type: IdentityProviderBase
    print(idp.display_name)
