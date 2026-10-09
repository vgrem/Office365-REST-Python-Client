"""Read list items page by page (server-driven paging).

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.collection import ListItemCollection
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Read list items page by page")
    parser.add_argument("--list-title", default="Documents", help="list title")
    parser.add_argument("--page-size", type=int, default=1000, help="items per page")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    target = ctx.web.lists.get_by_title(args.list_title)

    def print_page(items: ListItemCollection) -> None:
        print(f"Items read: {len(items)}")

    target.items.paged(args.page_size, page_loaded=print_page).get().execute_query()
    print(f"Loaded {len(target.items)} item(s); has next page: {target.items.has_next}")


if __name__ == "__main__":
    main()
