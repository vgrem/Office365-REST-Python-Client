"""
List Azure AD directory audit logs via Microsoft Graph.

https://learn.microsoft.com/en-us/graph/api/directoryaudit-list
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="List Azure AD directory audit logs")
    parser.add_argument("--top", type=int, default=10, help="number of records to fetch")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    audits = client.audit_logs.directory_audits.top(args.top).get().execute_query()
    for audit in audits:
        print(f"{audit.activity_datetime}: {audit.activity_display_name} ({audit.category})")


if __name__ == "__main__":
    main()
