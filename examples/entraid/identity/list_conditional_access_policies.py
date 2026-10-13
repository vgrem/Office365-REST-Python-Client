"""
List conditional access policies.

Conditional access policies are custom rules that define an access scenario —
who is allowed, under which conditions, and what access is granted or blocked.

Requires application permission ``Policy.Read.All``. Not every tenant grants it;
the script reports a denied request and exits 0.

Reference:
    https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-list-policies
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    client = _client()
    try:
        policies = client.identity.conditional_access.policies.get().execute_query()
    except ClientRequestException as e:
        print(f"Conditional access policies are not available with these credentials:\n  {e}")
        return

    print(f"Conditional access policies ({len(policies)}):")
    for policy in policies:
        print(
            f"  {policy.display_name or '?':50s}  state: {policy.state.name:10s}  "
            f"created: {policy.created_datetime:%Y-%m-%d}"
        )


if __name__ == "__main__":
    main()
