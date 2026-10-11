"""
Update an incident status — set classification, status, or assign
to an analyst.

Requires delegated permission ``Incidents.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-incident-update
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

incident_id = input("Incident ID: ").strip()
incident = client.security.incidents[incident_id].get().execute_query()

print(f"Current: {incident.display_name}  [{incident.status}]  [{incident.severity}]")

incident.set_property("status", "active")
incident.set_property("classification", "truePositive")
incident.set_property("determination", "malware")
incident.update().execute_query()
print("Updated: status=active, classification=truePositive, determination=malware")
