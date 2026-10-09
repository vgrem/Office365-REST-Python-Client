"""Save a list as a template in the list template gallery.

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Save a list as a template")
    parser.add_argument("--list-title", default="Site Pages", help="list title")
    parser.add_argument("--file-name", default="SitePages.stp", help="template file name (.stp)")
    parser.add_argument("--description", default="", help="template description")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    ctx.web.lists.get_by_title(args.list_title).save_as_template(
        args.file_name, args.list_title, args.description, True
    ).execute_query()
    print(f"Saved '{args.list_title}' as template '{args.file_name}'")


if __name__ == "__main__":
    main()
