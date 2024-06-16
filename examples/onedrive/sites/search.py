"""
Search across a SharePoint tenant for sites that match keywords provided.

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/site_search?view=odsp-graph-online
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
sites = client.sites.search("team").execute_query()
for site in sites:
    print("Site url: {0}".format(site.web_url))
