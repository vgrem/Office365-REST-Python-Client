"""
Get site by url

https://learn.microsoft.com/en-us/graph/api/site-get?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_team_site_url, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
site = client.sites.get_by_url(test_team_site_url).get().execute_query()
print("Site Id: {0}".format(site.id))
