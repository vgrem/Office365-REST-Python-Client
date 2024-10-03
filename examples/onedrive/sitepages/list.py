"""
Get the collection of sitePage objects from the site pages list in a site.

https://learn.microsoft.com/en-us/graph/api/sitepage-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_team_site_url, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
site = client.sites.get_by_url(test_team_site_url)
pages = site.pages.get().execute_query()
for page in pages:
    print("Page url: {0}".format(page))
