"""
eDiscovery — list the review sets of a case.

A review set holds the documents collected by a search, after they have been
exported into it for review. This is a read-only inventory of what has been
collected so far.

    python review_sets.py
    python review_sets.py --case-id <id>

Requires the application permission ``eDiscovery.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-ediscoverycase-list-reviewsets
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException
from tests.settings import client_id, client_secret, tenant

_SCOPE = "eDiscovery.ReadWrite.All"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description="List eDiscovery review sets")
    parser.add_argument("--case-id", help="eDiscovery case id (default: the first case)")
    args = parser.parse_args()

    client = _client()
    try:
        cases = client.security.cases.ediscovery_cases.get().execute_query()
        if not cases:
            print("No eDiscovery cases found.")
            return

        case = next((c for c in cases if c.id == args.case_id), None) if args.case_id else cases[0]
        if case is None:
            print(f"eDiscovery case '{args.case_id}' not found.")
            return

        review_sets = case.review_sets.get().execute_query()
        print(f"Review sets for '{case.get_property('displayName')}' ({len(review_sets)}):")
        for review_set in review_sets:
            print(f"  {review_set.get_property('displayName') or '(unnamed)':40s}  id: {review_set.id}")
    except AccessDeniedException as exc:
        print(f"Access denied: {exc.message}")
        print(f"Grant the application permission {_SCOPE} to the app registration and re-run.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
