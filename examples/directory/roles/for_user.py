"""
List the directory roles for the user.

https://learn.microsoft.com/en-us/graph/api/directoryrole-list?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
result = client.me.member_of.get().execute_query()
role_template_ids = [
    o.properties.get("roleTemplateId", None)
    for o in result
    if o.properties.get("roleTemplateId", None)
]
result = client.directory_roles.get().execute_query()
for role in result:
    if role.properties.get("roleTemplateId", None) in role_template_ids:
        print(role)
