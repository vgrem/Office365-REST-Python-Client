"""
Group lifecycle policies — list them and manage a group's expiration.

A lifecycle policy makes Microsoft 365 groups expire unless their owners renew
them, so stale groups get cleaned up automatically.

Requires application permission ``Group.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/resources/grouplifecyclepolicy
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="List and apply group lifecycle policies")
    parser.add_argument("--group", help="group display name to add to the first policy")
    parser.add_argument("--renew", action="store_true", help="renew the group instead of adding it")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    policies = client.group_lifecycle_policies.get().execute_query()
    print(f"Lifecycle policies ({len(policies)}):")
    for policy in policies:
        print(
            f"  lifetime: {policy.group_lifetime_in_days or '?'} days  "
            f"managed: {policy.managed_group_types or '-'}  "
            f"notify: {policy.alternate_notification_emails or '-'}"
        )

    if not args.group or not policies:
        return
    group = client.groups.find_by_name(args.group, required=True).execute_query()
    if group.id is None:
        print(f"Group '{group.display_name}' has no id.")
        return
    if args.renew:
        group.renew().execute_query()
        print(f"\nRenewed '{group.display_name}'.")
    else:
        policies[0].add_group(group_id=group.id).execute_query()
        print(f"\nAdded '{group.display_name}' to the first lifecycle policy.")


if __name__ == "__main__":
    main()
