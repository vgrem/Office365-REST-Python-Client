"""
Access reviews - list review definitions and their instances.

Access reviews let reviewers periodically attest who still needs access to a
group or application. This script walks the resource tree exposed by the
library:

    access_reviews.definitions -> definition.instances

Use it to audit what is currently under review and to see which review
instances are still open.

Requires application permission ``AccessReview.Read.All`` (or delegated).
Not every tenant grants it; the script reports a denied request and exits 0.

Reference:
    https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview
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
    access_reviews = client.identity_governance.access_reviews

    try:
        definitions = access_reviews.definitions.top(args.limit).get().execute_query()
    except ClientRequestException as e:
        print(f"Access reviews are not available with these credentials:\n  {e}")
        return

    print(f"Access review definitions ({len(definitions)}):\n")
    for definition in definitions:
        print(f"  {definition.display_name}  status={definition.status or '?'}  by={definition.created_by}")
        for instance in definition.instances.get().execute_query():
            print(
                f"    {instance.start_date_time:%Y-%m-%d} -> {instance.end_date_time:%Y-%m-%d}  status={instance.status}"
            )

    history = access_reviews.history_definitions.get().execute_query()
    print(f"\nHistory definitions ({len(history)}):")
    for definition in history:
        print(f"  {definition.display_name}  status={definition.status.name}  by={definition.created_by}")


if __name__ == "__main__":
    main()
