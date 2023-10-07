"""
Demonstrates how to retrieve a lookup field values from SharePoint List
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

list_tasks = ctx.web.lists.get_by_title("Company Tasks")
items = (
    list_tasks.items.get()
    .select(
        [
            "*",
            "AssignedTo/Id",
            "AssignedTo/Title",
            "Predecessors/Id",
            "Predecessors/Title",
        ]
    )
    .expand(["AssignedTo", "Predecessors"])
    .top(10)
    .execute_query()
)
for item in items:
    assigned_to = item.properties.get("AssignedTo", {}).get("Id", None)
    predecessors_ids = [
        v.get("Id", None) for k, v in item.properties.get("Predecessors", {}).items()
    ]
    print(
        "AssignedTo Id: {0}, Predecessors Ids: {1}".format(
            assigned_to, predecessors_ids
        )
    )
