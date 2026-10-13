"""
List all registered applications.

Retrieves the first 100 app registrations in the tenant, showing
the display name, app (client) ID, and creation date.

https://learn.microsoft.com/en-us/graph/api/application-list

https://learn.microsoft.com/en-us/graph/api/resources/application

Requires delegated permission ``Application.Read.All`` or ``Application.ReadWrite.All``.
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = (
    GraphClient(tenant=tenant)
    .with_client_secret(client_id, client_secret)
    .require_application_permission(
        "Application.Read.All",
        "Application.ReadWrite.OwnedBy",
        "Application.ReadWrite.All",
        "Directory.Read.All",
    )
)

apps = client.applications.select(["id", "displayName", "appId", "createdDateTime"]).top(100).get().execute_query()

print(apps.to_string())
