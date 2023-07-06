"""
Get a collection of sites.

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/site_list_subsites?view=odsp-graph-online
"""

from office365.graph_client import GraphClient
from office365.onedrive.sites.site import Site
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
sites = client.sites.paged(100).get().execute_query()
for i, site in enumerate(sites):  # type: int, Site
    print("({0} of {1}) Site url: {2}".format(i+1, len(sites), site.web_url))
print(len(sites))
