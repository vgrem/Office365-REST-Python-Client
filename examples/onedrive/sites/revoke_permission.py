"""
Revokes permissions from a site.

https://learn.microsoft.com/en-us/graph/api/site-delete-permission?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import (
    test_client_credentials,
    test_client_id,
    test_client_secret,
    test_team_site_url,
    test_tenant,
)

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)

app = client.applications.get_by_app_id(test_client_credentials.clientId)
site = client.sites.get_by_url(test_team_site_url)
site.permissions.delete_all().execute_query()
