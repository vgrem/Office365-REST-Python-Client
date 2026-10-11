"""
eDiscovery — run a minimal case workflow end to end, then clean up.

Creates an eDiscovery (Premium) case, adds a custodian and defines a search,
then deletes the case. This is the smallest complete case: holds, review sets
and exports all hang off a case, so it is the right starting point.

    python cases.py
    python cases.py --custodian investigator@contoso.com --query "subject:'confidential'"
    python cases.py --keep

Requires the application permission ``eDiscovery.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-post-ediscoverycases
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException
from tests import create_unique_name
from tests.settings import client_id, client_secret, tenant, user_principal

_SCOPE = "eDiscovery.ReadWrite.All"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal eDiscovery case workflow")
    parser.add_argument("--name", help="Case name (default: a unique generated name)")
    parser.add_argument("--custodian", default=user_principal, help="Custodian UPN")
    parser.add_argument("--query", default="subject:'confidential'", help="Search query")
    parser.add_argument("--keep", action="store_true", help="Keep the case instead of deleting it")
    args = parser.parse_args()

    client = _client()
    case = None
    try:
        case = client.security.cases.ediscovery_cases.add(
            displayName=args.name or create_unique_name("SDK eDiscovery Case"),
            description="Investigation started from the Python client example",
        ).execute_query()
        print(f"Case:      {case.get_property('displayName')}  ({case.id})")

        custodian = case.custodians.add(email=args.custodian).execute_query()
        print(f"Custodian: {custodian.email}")

        search = case.searches.add(
            displayName=create_unique_name("SDK Search"),
            contentQuery=args.query,
        ).execute_query()
        print(f"Search:    {search.get_property('displayName')}  ({search.id})")
    except AccessDeniedException as exc:
        print(f"Access denied: {exc.message}")
        print(f"Grant the application permission {_SCOPE} to the app registration and re-run.")
        raise SystemExit(0) from None

    if args.keep:
        print(f"\nCase retained — open it in the Purview portal (id {case.id}).")
    elif case is not None:
        case.delete_object().execute_query()
        print("\nCase deleted.")


if __name__ == "__main__":
    main()
