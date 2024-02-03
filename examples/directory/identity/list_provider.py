"""
Get a collection of identity provider resources that are configured for a tenant

https://learn.microsoft.com/en-us/graph/api/identitycontainer-list-identityproviders?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
providers = client.identity.identity_providers.get().execute_query()
for idp in providers:
    print(idp.display_name)
