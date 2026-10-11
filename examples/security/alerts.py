"""
List alerts from Microsoft 365 Defender (v2 API).

Requires delegated permission ``SecurityAlert.Read.All`` or
``SecurityAlert.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-list-alerts_v2?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

alerts = client.security.alerts_v2.top(20).get().execute_query()
print(f"Alerts ({len(alerts)}):")
for alert in alerts:
    print(f"  {alert}")
