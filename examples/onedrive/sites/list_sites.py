"""
Get a collection of sites.

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/site_list_subsites?view=odsp-graph-online
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
sites = client.sites.paged(100).get().execute_query()
for site in sites:
    print("Site url: {0}".format(site.web_url))
