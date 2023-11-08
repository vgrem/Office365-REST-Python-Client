"""
Revokes permissions from a site.

https://learn.microsoft.com/en-us/graph/api/site-delete-permission?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_credentials, test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)

app = client.applications.get_by_app_id(test_client_credentials.clientId)
site = client.sites.get_by_url(test_team_site_url)
site.permissions.delete(["write"], app).execute_query()
# site.permissions.delete_all().execute_query()
