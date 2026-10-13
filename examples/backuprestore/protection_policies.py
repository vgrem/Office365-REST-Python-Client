"""
List protection policies for every Backup Storage workload.

Protection policies define what Microsoft 365 data is protected, when and for
how long. Each workload (OneDrive for Business, SharePoint, Exchange) has its
own policy collection and its own inclusion-rule collection.

Requires delegated or application permission ``BackupRestore-Control.Read.All``.
On an unlicensed tenant the call is denied and a short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-list-onedriveforbusinessprotectionpolicies
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant

if TYPE_CHECKING:
    from office365.directory.protection.policy.base import ProtectionPolicyBase


def _print_policy(policy: ProtectionPolicyBase, expressions: List[Optional[str]]) -> None:
    print(f"  {policy.display_name or '(unnamed)'}")
    print(f"    status:  {policy.status}")
    print(f"    enabled: {policy.is_enabled}")
    print(f"    rules:   {len(expressions)}")
    for expression in expressions:
        print(f"      - {expression or '(no expression)'}")


def _run(client: GraphClient) -> None:
    backup = client.solutions.backup_restore

    policies = backup.one_drive_for_business_protection_policies.get().execute_query()
    print(f"OneDrive for Business protection policies ({len(policies)}):")
    for policy in policies:
        rules = policy.drive_inclusion_rules.get().execute_query()
        _print_policy(policy, [rule.drive_expression for rule in rules])

    policies = backup.sharepoint_protection_policies.get().execute_query()
    print(f"\nSharePoint protection policies ({len(policies)}):")
    for policy in policies:
        rules = policy.site_inclusion_rules.get().execute_query()
        _print_policy(policy, [rule.site_expression for rule in rules])

    policies = backup.exchange_protection_policies.get().execute_query()
    print(f"\nExchange protection policies ({len(policies)}):")
    for policy in policies:
        rules = policy.mailbox_inclusion_rules.get().execute_query()
        _print_policy(policy, [rule.mailbox_expression for rule in rules])


def main() -> None:
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        _run(client)
    except ClientRequestException as err:
        print("Microsoft 365 Backup Storage is not available on this tenant.")
        print("It is a paid add-on and must be enabled; see README.md -> 'Licensing'.")
        print(f"\nServer response: {err}")


if __name__ == "__main__":
    main()
