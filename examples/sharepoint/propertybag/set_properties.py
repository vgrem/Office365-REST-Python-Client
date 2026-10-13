"""
Set a property bag value on a web.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Set a web property bag value")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    parser.add_argument("--key", default="Custom_MyKey", help="property bag key")
    parser.add_argument("--value", default="MyValue", help="property bag value")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_username_and_password(tenant, client_id, username, password)
    web = ctx.web
    web.set_property("AllProperties", {args.key: args.value}).update().execute_query()
    print(f"Property bag updated: {args.key}")


if __name__ == "__main__":
    main()
