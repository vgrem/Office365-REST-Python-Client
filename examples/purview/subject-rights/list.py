"""
Subject rights — list the data subject requests in the tenant.

Reads the request queue: what each request is for, the stage it has reached, and
the internal due date. Use it as a compliance progress check.

    python list.py
    python list.py --status active

Requires the application permission ``SubjectRightsRequest.Read.All``.

https://learn.microsoft.com/en-us/graph/api/security-list-subjectrightsrequests
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import AccessDeniedException
from tests.settings import client_id, client_secret, tenant

_SCOPE = "SubjectRightsRequest.Read.All"


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description="List subject rights requests")
    parser.add_argument("--status", help="Only requests in this stage (e.g. active, closed)")
    args = parser.parse_args()

    client = _client()
    try:
        requests = client.security.subject_rights_requests.get().execute_query()
        if args.status:
            requests = [request for request in requests if request.get_property("status") == args.status]

        print(f"Subject rights requests ({len(requests)}):")
        for request in requests:
            name = request.get_property("displayName") or "(unnamed)"
            kind = request.get_property("type")
            status = request.get_property("status")
            print(f"  {name:40s}  type={kind}  status={status}")
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
