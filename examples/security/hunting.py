"""
Run an advanced hunting KQL query against Microsoft Defender XDR data.

Hunting reads the raw tables detections are built from — ``AlertInfo``,
``DeviceProcessEvents``, ``EmailEvents``, ``IdentityLogonEvents`` and more — and
returns rows you shape with ``project`` / ``summarize`` / ``take``. This example
lists recent alert records; swap the query for your own.

Requires delegated permission ``ThreatHunting.Read.All``.

https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

#: A small, schema-valid query; replace with your own KQL.
QUERY = """
AlertInfo
| where Timestamp > ago(7d)
| project Timestamp, Title, Severity, Category
| take 20
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an advanced hunting KQL query")
    parser.add_argument("--query", default=QUERY, help="KQL query to run (default: recent AlertInfo rows)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    response = client.security.run_hunting_query(args.query).execute_query().value
    columns = [column.name for column in response.schema]
    rows = list(response.results)
    print(f"{len(rows)} row(s):")
    for row in rows:
        values = dict(row)  # HuntingRowResult yields (column, value) pairs
        print("  " + "  ".join(f"{name}={values.get(name)}" for name in columns))


if __name__ == "__main__":
    main()
