from examples import acquire_token_by_username_password, sample_tenant_prefix
from office365.graph_client import GraphClient

file_abs_url = "https://{0}.sharepoint.com/sites/team/Shared Documents/big_buck_bunny.mp4".format(sample_tenant_prefix)

client = GraphClient(acquire_token_by_username_password)
file_item = client.shares.by_url(file_abs_url).drive_item.get().execute_query()
print(file_item.web_url)
