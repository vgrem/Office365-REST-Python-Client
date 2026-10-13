"""
Graph change notifications - subscribe to resource changes and manage the
subscription lifecycle.

Subscriptions let your app receive push notifications when Microsoft Graph
resources change. The notification URL must be reachable over HTTPS and answer
Graph's validation request (echo ``validationToken``), so creating a
subscription is opt-in here with ``--apply``.

Requires the delegated/application permission that matches ``--resource``
(for example ``User.Read.All`` for ``users``).

Reference:
    https://learn.microsoft.com/en-us/graph/api/resources/subscription
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

DEFAULT_NOTIFICATION_URL = "https://example.com/graph-notifications"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notification-url", default=DEFAULT_NOTIFICATION_URL, help="HTTPS webhook endpoint")
    parser.add_argument("--resource", default="users", help="resource path to watch (e.g. users, me/mailFolders)")
    parser.add_argument("--change-type", default="updated,created,deleted", help="comma-separated change types")
    parser.add_argument("--hours", type=int, default=12, help="lifetime of the subscription, in hours")
    parser.add_argument("--apply", action="store_true", help="create/renew/delete (default: list only)")
    args = parser.parse_args()

    client = _client()
    subscription = None

    if args.apply:
        expiration = datetime.now(timezone.utc) + timedelta(hours=args.hours)
        subscription = client.subscriptions.add(
            change_type=args.change_type,
            notification_url=args.notification_url,
            resource=args.resource,
            expiration=expiration,
            client_state="sdk-example",
        ).execute_query()
        print(
            f"Created subscription {subscription.id}  resource={subscription.resource}  "
            f"expires={subscription.expiration_datetime}"
        )

        renewal = datetime.now(timezone.utc) + timedelta(hours=args.hours * 2)
        subscription.expiration_datetime = renewal
        subscription.update().execute_query()
        print(f"Renewed subscription {subscription.id} -> expires={subscription.expiration_datetime}")

    subscriptions = client.subscriptions.get().execute_query()
    print(f"\nActive subscriptions ({len(subscriptions)}):")
    for item in subscriptions:
        print(f"  {item.id:45s}  resource={item.resource or '?':30s}  expires={item.expiration_datetime:%Y-%m-%d %H:%M}")

    if subscription is not None:
        subscription.delete_object().execute_query()
        print(f"\nDeleted subscription {subscription.id}.")


if __name__ == "__main__":
    main()
