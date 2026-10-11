"""
Get an incident with all its alerts expanded.

Shows the full picture — incident metadata plus each alert's
title, severity, status, and category.

Requires delegated permission ``Incidents.Read.All``.

https://learn.microsoft.com/en-us/graph/api/security-incident-get
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

incident_id = input("Incident ID: ").strip()
incident = client.security.incidents[incident_id].expand(["alerts"]).get().execute_query()

print(f"\nIncident: {incident.display_name}")
print(f"  Status:     {incident.status}")
print(f"  Severity:   {incident.severity}")
print(f"  Tags:       {incident.tags or []}")
print(f"  Alerts ({len(incident.alerts)}):\n")
for a in incident.alerts:
    print(f"    [{a.severity or '?':10s}] [{a.status or '?':15s}] {a.title or '(no title)'}")
