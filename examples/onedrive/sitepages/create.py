"""
Create a new sitePage in the site pages list in a site.

https://learn.microsoft.com/en-us/graph/api/sitepage-create?view=graph-rest-beta
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_team_site_url, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
site = client.sites.get_by_url(test_team_site_url)
page = site.pages.add("test456").execute_query()
print("Page url: {0}".format(page))
