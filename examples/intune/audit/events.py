"""
Audit events: who changed what in Intune, and when.

Intune writes an audit event for every administrative change — policy edits,
device actions, role changes. Each event carries an actor, the resources it
touched and the result, which makes it the first stop for "why did this
setting change?" investigations.

    python events.py                       # last 7 days
    python events.py --days 30 --category DeviceConfiguration
    python events.py --details              # include the affected resources

Requires delegated permission ``DeviceManagementApps.Read.All`` (or an Intune
administrative role).

https://learn.microsoft.com/en-us/graph/api/intune-auditing-auditevent-list
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def actor_name(event) -> str:
    actor = event.actor
    if actor is None:
        return "?"
    return actor.userPrincipalName or actor.applicationDisplayName or "?"


def main() -> None:
    parser = argparse.ArgumentParser(description="Browse Intune audit events")
    parser.add_argument("--days", type=int, default=7, help="How many days back to look (default: 7)")
    parser.add_argument("--category", help="Restrict to an audit category, e.g. DeviceConfiguration")
    parser.add_argument("--details", action="store_true", help="Also list the affected resources")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = client.device_management.audit_events.filter(f"activityDateTime ge {since}").order_by(
        "activityDateTime desc"
    )
    if args.category:
        query = query.filter(f"category eq '{args.category}'")

    try:
        events = list(query.get_all().execute_query())
    except ClientRequestException as exc:
        print(f"[skipped] {exc.code}: {exc.message}")
        print("Audit events need an Intune role and DeviceManagementApps.Read.All (or similar).")
        return

    print(f"{len(events)} audit event(s) in the last {args.days} day(s):")
    for event in events:
        when = event.activity_date_time.strftime("%Y-%m-%d %H:%M") if event.activity_date_time else "?"
        print(f"  {when}  {(event.activity or '?'):35s} by {actor_name(event)}  -> {event.activity_result or '?'}")
        if args.details:
            for resource in event.resources or []:
                print(f"      {resource.auditResourceType or '?'}: {resource.displayName or '?'}")


if __name__ == "__main__":
    main()
