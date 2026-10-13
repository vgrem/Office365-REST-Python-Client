"""
Get property bag values on a web.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Read web property bag values")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    parser.add_argument("--prefix", default="Custom_", help="only print keys with this prefix")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_username_and_password(tenant, client_id, username, password)
    web = ctx.web.get().execute_query()

    all_props = web.all_properties.get().execute_query()
    matches = [(key, value) for key, value in all_props.properties.items() if key.startswith(args.prefix)]
    if not matches:
        print(f"No property bag keys with prefix '{args.prefix}'.")
        return
    for key, value in matches:
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
