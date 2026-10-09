"""
Get a folder by its site-relative path (``Web.folders.get_by_path``).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Get a folder by path")
    parser.add_argument("--folder-path", default="Documents", help="site-relative folder path")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.folders.get_by_path(args.folder_path).get().execute_query()
    print(folder.server_relative_url)


if __name__ == "__main__":
    main()
