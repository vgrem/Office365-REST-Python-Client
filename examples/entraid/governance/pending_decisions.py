"""
Access reviews - list decisions that are still pending.

For every review instance that is still in progress, this walks its decisions
and prints the ones a reviewer has not acted on yet (``NotReviewed``). That is
the actionable queue for access certification.

Requires application permission ``AccessReview.Read.All`` (or delegated).
Not every tenant grants it; the script reports a denied request and exits 0.

Reference:
    https://learn.microsoft.com/en-us/graph/api/accessreviewinstance-list-decisions
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
    parser.add_argument("--limit", type=int, default=10, help="max definitions to inspect")
    args = parser.parse_args()

    client = _client()
    definitions = client.identity_governance.access_reviews.definitions.top(args.limit)

    try:
        definitions = definitions.get().execute_query()
    except ClientRequestException as e:
        print(f"Access reviews are not available with these credentials:\n  {e}")
        return

    print(f"Pending decisions across {len(definitions)} definition(s):\n")
    total = 0
    for definition in definitions:
        for instance in definition.instances.get().execute_query():
            if instance.status != "InProgress":
                continue
            for decision in instance.decisions.get().execute_query():
                if decision.decision != "NotReviewed":
                    continue
                print(f"  {definition.display_name}  user={decision.principal}")
                total += 1

    if total == 0:
        print("  (nothing pending)")


if __name__ == "__main__":
    main()
