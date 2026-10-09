"""
List Azure AD sign-in logs via Microsoft Graph.

https://learn.microsoft.com/en-us/graph/api/signin-list
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="List Azure AD sign-in logs")
    parser.add_argument("--top", type=int, default=10, help="number of records to fetch")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    signins = client.audit_logs.signins.top(args.top).get().execute_query()
    for signin in signins:
        status = signin.status
        error_code = status.errorCode if status else None
        failure_reason = status.failureReason if status else None
        print(
            f"{signin.created_datetime}: {signin.user_display_name} "
            f"(errorCode={error_code}, failureReason={failure_reason})"
        )


if __name__ == "__main__":
    main()
