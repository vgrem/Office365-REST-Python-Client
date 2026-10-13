"""
Disables SSL certificate verification for SharePoint requests.

⚠️ WARNING: Only use this for testing with self-signed certificates.
Never disable SSL verification in production.

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Disable SSL verification (dev/test only)")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    args = parser.parse_args()

    ctx = (
        ClientContext(args.site_url)
        .with_username_and_password(
            tenant=tenant,
            client_id=client_id,
            username=username,
            password=password,
        )
        .with_transport(verify=False)
    )

    web = ctx.web.get().execute_query()
    print(web.url)


if __name__ == "__main__":
    main()
