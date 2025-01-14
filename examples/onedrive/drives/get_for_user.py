"""
Demonstrates how to get a drive for a user.
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
site = (
    client.users.get_by_principal_name(test_user_principal_name)
    .get_my_site()
    .execute_query()
)
print("Drive url: {0}".format(site.web_url))
