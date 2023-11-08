"""
Lists site permissions.

"""

from office365.graph_client import GraphClient
from tests import test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)

site = client.sites.get_by_url(test_team_site_url)
permissions = site.permissions.get().execute_query()
for perm in permissions:
    print(perm.granted_to)
