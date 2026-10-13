"""
List all hub sites the current user can access.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/hubsites
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="List all hub sites the current user can access")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    hub_sites = ctx.hub_sites.get().execute_query()
    for hub in hub_sites:
        print(f"{hub.title}  ({hub.site_url})")


if __name__ == "__main__":
    main()
