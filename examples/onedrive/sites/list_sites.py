"""
Get a collection of sites.

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/site_list_subsites?view=odsp-graph-online
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
sites = client.sites.paged(100).get().execute_query()
for site in sites:
    print("Site url: {0}".format(site.web_url))
