"""
List incidents from Microsoft 365 Defender.

Requires delegated permission ``Incidents.Read.All`` or
``Incidents.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-list-incidents?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

incidents = client.security.incidents.get().execute_query()
for inc in incidents:
    print(f"  [{inc.severity or 'N/A':10s}] [{inc.status or 'unknown':15s}] {inc.display_name}")
