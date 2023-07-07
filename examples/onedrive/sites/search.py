"""
Search across a SharePoint tenant for sites that match keywords provided.



https://learn.microsoft.com/en-us/onedrive/developer/rest-api/api/site_search?view=odsp-graph-online
"""

from office365.graph_client import GraphClient
from office365.onedrive.sites.site import Site
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
sites = client.sites.search("team").execute_query()
for site in sites:  # type: Site
    print("Site url: {0}".format(site.web_url))
