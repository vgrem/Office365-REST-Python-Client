"""
Update an incident — set its status, classification or determination.

Writes are **opt-in**: without ``--apply`` the script only shows what it *would*
change, so it is safe to run. With no ``--incident-id`` it targets the first
active incident.

Requires delegated permission ``Incidents.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-incident-update
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

#: Allowed values per the Security API.
STATUSES = ("active", "resolved", "redirected")
CLASSIFICATIONS = ("unknown", "falsePositive", "truePositive", "informationalExpectedActivity")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update an incident (dry-run unless --apply)")
    parser.add_argument("--incident-id", help="incident id (default: the first active incident)")
    parser.add_argument("--status", default="active", choices=STATUSES)
    parser.add_argument("--classification", default="truePositive", choices=CLASSIFICATIONS)
    parser.add_argument("--determination", default="malware", help="e.g. malware, phishing, suspiciousActivity")
    parser.add_argument("--apply", action="store_true", help="actually perform the update")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    incident_id = args.incident_id
    if not incident_id:
        active = client.security.incidents.filter("status eq 'active'").get().execute_query()
        if not active:
            print("No active incidents found; pass --incident-id.")
            return
        incident_id = active[0].id

    incident = client.security.incidents[incident_id].get().execute_query()
    print(f"Current: {incident.display_name}  [{incident.status}]  [{incident.severity}]")
    print(f"Planned: status={args.status} classification={args.classification} determination={args.determination}")

    if not args.apply:
        print("Dry run — re-run with --apply to write.")
        return

    incident.set_property("status", args.status)
    incident.set_property("classification", args.classification)
    incident.set_property("determination", args.determination)
    incident.update().execute_query()
    print("Updated.")


if __name__ == "__main__":
    main()
