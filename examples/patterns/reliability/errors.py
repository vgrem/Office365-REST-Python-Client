"""
Read a Microsoft Graph error and retry what is retryable.

Graph failures surface as a ``ClientRequestException`` carrying the HTTP status
and a structured ``error`` object. The library parses it for you — ``code``,
``message``, ``inner_error``, plus SharePoint's ``hresult`` / ``error_type`` —
and dispatches to a concrete subclass when one matches (e.g.
``DuplicatedObjectException``). This example shows the shape and how to branch.

Requires delegated permission ``Files.Read``.

https://learn.microsoft.com/en-us/graph/errors
https://learn.microsoft.com/en-us/graph/throttling
"""

from __future__ import annotations

import argparse
from http import HTTPStatus

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username


def main() -> None:
    argparse.ArgumentParser(description="Inspect a Microsoft Graph error response").parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    try:
        client.me.drive.items["this-item-does-not-exist"].get().execute_query()
    except ClientRequestException as ex:
        status = getattr(ex.response, "status_code", None)
        retry_after = (getattr(ex.response, "headers", None) or {}).get("Retry-After")
        print(f"HTTP {status}")
        print(f"  code:        {ex.code}")
        print(f"  message:     {ex.message}")
        print(f"  inner_error: {ex.inner_error}")
        print(f"  retry-after: {retry_after}")

        # Branch on the reason, not on a string of the message:
        if status == HTTPStatus.NOT_FOUND:
            print("  -> not found; fall back to another id or create the item")
        elif status == HTTPStatus.TOO_MANY_REQUESTS:
            print(f"  -> throttled; sleep {retry_after or 'a moment'}s and retry")
        elif status == HTTPStatus.FORBIDDEN:
            print("  -> forbidden; the app is missing a scope or admin consent")
        elif status == HTTPStatus.UNAUTHORIZED:
            print("  -> unauthenticated; refresh the token")
        else:
            raise


if __name__ == "__main__":
    main()
