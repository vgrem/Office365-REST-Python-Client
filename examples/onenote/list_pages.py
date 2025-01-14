"""
Retrieve a list of page objects

https://learn.microsoft.com/en-us/graph/api/onenote-list-pages?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
section = (
    client.me.onenote.sections.first("displayName eq 'Quick Notes'")
    .get()
    .execute_query()
)
pages = section.pages.get().execute_query()
for page in pages:
    print(page.title)
