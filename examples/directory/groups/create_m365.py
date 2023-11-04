"""
Create a Microsoft 365 group

The following example creates a Microsoft 365 group. Because the owners have not been specified,
the calling user is automatically added as the owner of the group.

https://learn.microsoft.com/en-us/graph/api/group-post-groups?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password

grp_name = create_unique_name("Group")
client = GraphClient(acquire_token_by_username_password)
group = client.groups.create_m365(grp_name).execute_query()

# clean up resources
group.delete_object(True).execute_query()
