"""
Get an incident with all its alerts expanded.

Shows the full picture — incident metadata plus each alert's title, severity,
status and category. With no ``--incident-id`` it picks the first active incident.

Requires delegated permission ``Incidents.Read.All``.

https://learn.microsoft.com/en-us/graph/api/security-incident-get
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Show an incident and its alerts")
    parser.add_argument("--incident-id", help="incident id (default: the first active incident)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    incident_id = args.incident_id
    if not incident_id:
        active = client.security.incidents.filter("status eq 'active'").get().execute_query()
        if not active:
            print("No active incidents found; pass --incident-id.")
            return
        incident_id = active[0].id

    incident = client.security.incidents[incident_id].expand(["alerts"]).get().execute_query()
    print(f"\nIncident: {incident.display_name}")
    print(f"  Status:     {incident.status}")
    print(f"  Severity:   {incident.severity}")
    print(f"  Tags:       {incident.tags or []}")
    print(f"  Alerts ({len(incident.alerts)}):\n")
    for alert in incident.alerts:
        print(f"    [{alert.severity or '?':10s}] [{alert.status or '?':15s}] {alert.title or '(no title)'}")


if __name__ == "__main__":
    main()
