"""
Add a child navigation node (sub-menu) under an existing Quick Launch node.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/navigation-api-reference
"""

import argparse
import sys

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.navigation.nodes.creationinformation import NavigationNodeCreationInformation
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Add a child node under a Quick Launch node")
    parser.add_argument("--parent-title", default="", help="parent node title (default: first node)")
    parser.add_argument("--title", default="Child page", help="title of the new child node")
    parser.add_argument(
        "--url",
        default="https://learn.microsoft.com/en-us/sharepoint/dev/apis/navigation-api-reference",
        help="URL the child node links to (external links are safest)",
    )
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    nav = ctx.web.navigation.quick_launch.get().execute_query()
    if not nav:
        sys.exit("No navigation nodes found.")

    if args.parent_title:
        parent = next((n for n in nav if n.title == args.parent_title), None)
    else:
        parent = nav[0]
    if parent is None:
        sys.exit(f"Parent node not found: {args.parent_title}")

    url = args.url
    child_info = NavigationNodeCreationInformation(Title=args.title, Url=url, AsLastNode=True)
    child = parent.children.add(child_info).execute_query()
    print(f"Child node added: {child.title} under {parent.title}")


if __name__ == "__main__":
    main()
