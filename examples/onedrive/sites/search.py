"""
Search across a SharePoint tenant for sites that match keywords provided.
"""

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.onedrive.sites.site import Site

client = GraphClient(acquire_token_by_client_credentials)
sites = client.sites.search("team").execute_query()
for site in sites:  # type: Site
    print("Site url: {0}".format(site.web_url))
