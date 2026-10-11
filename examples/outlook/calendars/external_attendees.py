"""
Find meetings with external attendees — attendees outside the tenant domain.

Governance: detect when users invite external guests, which may have compliance
implications. Reads the signed-in user's events, so it needs **delegated** auth.

Requires delegated permission ``Calendars.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-events
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

DISPLAY_LIMIT = 20


def main() -> None:
    parser = argparse.ArgumentParser(description="List meetings that include external attendees")
    parser.add_argument("--top", type=int, default=100, help="how many events to scan (default: 100)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    tenant_domain = tenant.split("@")[-1] if "@" in tenant else tenant

    events = client.me.events.top(args.top).get().execute_query()
    external = []
    for event in events:
        for attendee in event.attendees or []:
            address = attendee.emailAddress.address or ""
            if address and tenant_domain not in address:
                external.append((event.subject, attendee.emailAddress.name, address))
                break

    print(f"Meetings with external attendees: {len(external)}\n")
    for subject, name, address in external[:DISPLAY_LIMIT]:
        print(f"  {subject or '(no subject)':40s}  {name or '':20s}  {address}")
    if len(external) > DISPLAY_LIMIT:
        print(f"  ... and {len(external) - DISPLAY_LIMIT} more")


if __name__ == "__main__":
    main()
