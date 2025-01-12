"""
Username Password Authentication flow

https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
me = client.me.get().execute_query()
print(me.user_principal_name)
