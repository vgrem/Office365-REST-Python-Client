"""
List root sites across geographies in an organization.

https://learn.microsoft.com/en-us/graph/api/site-getallsites?view=graph-rest-1.0&tabs=http
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
sites = client.sites.get_all_sites().execute_query()
print("{0} sites was found".format(len(sites)))
