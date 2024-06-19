"""
List root sites across geographies in an organization.

https://learn.microsoft.com/en-us/graph/api/site-getallsites?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
sites = client.sites.get_all_sites().execute_query()
print("{0} sites was found".format(len(sites)))
