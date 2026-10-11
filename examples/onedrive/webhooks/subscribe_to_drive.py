"""
Receive push notifications when drive content changes.

Instead of polling a drive, Graph POSTs a notification to your HTTPS endpoint
when something changes. Subscribe to the drive root or a single item, pass a
``clientState`` secret so you can verify the caller, then renew before it expires
and remove it when done.

Requires delegated permission for the resource (``Files.Read.All`` for
``me/drive/root``) and a **publicly reachable HTTPS** endpoint that answers the
validation handshake.

https://learn.microsoft.com/en-us/graph/change-notifications-overview
https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/webhooks
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def _expiry(**delta: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(**delta)).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description="Subscribe a webhook to OneDrive changes")
    parser.add_argument("--notification-url", required=True, help="your HTTPS webhook endpoint")
    parser.add_argument("--resource", default="me/drive/root", help="resource to watch (default: the drive root)")
    parser.add_argument("--keep", action="store_true", help="keep the subscription after the demo")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    subscription = client.subscriptions.add(
        changeType="updated",
        notificationUrl=args.notification_url,
        resource=args.resource,
        expirationDateTime=_expiry(hours=12),
        clientState="verify-me",  # echoed back on every notification
    ).execute_query()
    print(f"Subscription {subscription.id} on {subscription.resource} expires {subscription.expiration_date_time}")

    # Graph expires subscriptions, so renew them on a schedule.
    subscription.set_property("expirationDateTime", _expiry(days=1))
    subscription.update().execute_query()
    print("Renewed for another day.")

    if not args.keep:
        subscription.delete_object().execute_query()
        print("Subscription removed.")


if __name__ == "__main__":
    main()
