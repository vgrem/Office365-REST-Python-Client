"""
Demonstrates how to construct and submit requests without a model involved.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-api
"""

import argparse
import json

from office365.sharepoint.request import SharePointRequest
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Submit a raw request without a model")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    parser.add_argument("--path", default="web/currentUser", help="relative REST path to request")
    args = parser.parse_args()

    request = SharePointRequest(args.site_url).with_username_and_password(
        tenant=tenant,
        client_id=client_id,
        username=username,
        password=password,
    )

    try:
        response = request.execute_request(args.path)
        parsed = json.loads(response.content)
        prop_val = parsed["d"]["UserPrincipalName"]
        print(f"UserPrincipalName: {prop_val}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
