"""
Get site by url
https://learn.microsoft.com/en-us/graph/api/site-get?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests import test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
site = client.sites.get_by_url(test_team_site_url).get().execute_query()
print("Site Id: {0}".format(site.id))
