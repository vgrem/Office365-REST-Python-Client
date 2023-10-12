"""
Get a collection of identity provider resources that are configured for a tenant

https://learn.microsoft.com/en-us/graph/api/identitycontainer-list-identityproviders?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
providers = client.identity.identity_providers.get().execute_query()
for idp in providers:
    print(idp.display_name)
