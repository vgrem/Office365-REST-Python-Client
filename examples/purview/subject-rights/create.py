"""
Subject rights — create a data subject request (GDPR / CCPA).

A subject rights request tracks one person's access, export or deletion request
from intake to fulfilment, including the internal due date that keeps the
organisation inside the statutory window.

    python create.py
    python create.py --email jane@contoso.com --type export --due-days 30

Requires the application permission ``SubjectRightsRequest.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-post-subjectrightsrequests
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import AccessDeniedException
from office365.security.subjectrightsrequests.data_subject import DataSubject
from tests.settings import client_id, client_secret, tenant

_SCOPE = "SubjectRightsRequest.ReadWrite.All"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a subject rights request")
    parser.add_argument("--email", default="user@contoso.com", help="Data subject email address")
    parser.add_argument("--type", default="export", choices=["export", "access", "delete", "tagForAction"])
    parser.add_argument("--due-days", type=int, default=30, help="Days until the internal due date")
    args = parser.parse_args()

    due = datetime.now(timezone.utc) + timedelta(days=args.due_days)
    client = _client()
    try:
        request = client.security.subject_rights_requests.add(
            type=args.type,
            displayName=f"Subject rights request — {args.email}",
            description="Created from the Python client example",
            internalDueDateTime=due.strftime("%Y-%m-%dT%H:%M:%SZ"),
            dataSubject=DataSubject(email=args.email),
        ).execute_query()
        print(f"Request created: {request.get_property('displayName')}  ({request.id})")
        print(f"  Type:   {request.get_property('type')}")
        print(f"  Status: {request.get_property('status')}")
        print(f"  Due:    {due.date()}")
    except AccessDeniedException as exc:
        print(f"Access denied: {exc.message}")
        print(f"Grant the application permission {_SCOPE} to the app registration and re-run.")
        raise SystemExit(0) from None
    except ClientRequestException as exc:
        print(f"{exc.code}: {exc.message}")
        print("The subject rights requests service may not be provisioned for this tenant.")
        raise SystemExit(0) from None


if __name__ == "__main__":
    main()
