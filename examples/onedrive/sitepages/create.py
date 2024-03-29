"""
Create a new sitePage in the site pages list in a site.

https://learn.microsoft.com/en-us/graph/api/sitepage-create?view=graph-rest-beta
"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
root_site = client.sites.root.get().execute_query()
page = root_site.pages.add("test").execute_query()
print("Page url: {0}".format(page))
