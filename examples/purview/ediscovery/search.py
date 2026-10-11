"""
eDiscovery — define a search that also covers partially indexed items.

Partially indexed items (unsupported file types, encrypted content, or items
the indexer could not parse) are invisible to a normal search but can still be
relevant to an investigation. A **non-custodial** search scoped with
`dataSourceScopes` is how you reach them.

This script creates a short-lived case and a search over all tenant mailboxes
and sites, prints the search id, then removes the case again.

    python search.py
    python search.py --query "*" --scopes allTenantMailboxes,allTenantSites
    python search.py --keep

Requires the application permission ``eDiscovery.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-ediscoverysearch
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException
from tests import create_unique_name
from tests.settings import client_id, client_secret, tenant

_SCOPE = "eDiscovery.ReadWrite.All"
_DEFAULT_SCOPES = "allTenantMailboxes,allTenantSites"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an eDiscovery non-custodial search")
    parser.add_argument("--query", default="*", help="Search query (default: everything)")
    parser.add_argument("--scopes", default=_DEFAULT_SCOPES, help="Comma-separated dataSourceScopes")
    parser.add_argument("--keep", action="store_true", help="Keep the case instead of deleting it")
    args = parser.parse_args()

    client = _client()
    case = None
    try:
        case = client.security.cases.ediscovery_cases.add(
            displayName=create_unique_name("Partially indexed scan"),
        ).execute_query()

        search = case.searches.add(
            displayName="Partially indexed items",
            contentQuery=args.query,
            dataSourceScopes=args.scopes,
        ).execute_query()
        print(f"Case:   {case.get_property('displayName')}  ({case.id})")
        print(f"Search: {search.get_property('displayName')}  ({search.id})")
        print(f"Scopes: {args.scopes}")
    except AccessDeniedException as exc:
        print(f"Access denied: {exc.message}")
        print(f"Grant the application permission {_SCOPE} to the app registration and re-run.")
        raise SystemExit(0) from None

    print("\nStart the estimate from the Purview portal (or POST /searches/{id}/estimateStatistics);")
    print("the operation's itemCount vs indexedItemCount reveals the partially indexed items.")

    if args.keep:
        print(f"\nCase retained — open it in the Purview portal (id {case.id}).")
    elif case is not None:
        case.delete_object().execute_query()
        print("\nCase deleted.")


if __name__ == "__main__":
    main()
