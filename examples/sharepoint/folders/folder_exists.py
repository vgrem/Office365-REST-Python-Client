"""
Determine whether a folder exists (without raising on a miss).

Uses the ``Exists`` property; an alternative is to try the request and handle
``FileNotFoundException`` (HTTP 404).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/folder-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Check whether a folder exists")
    parser.add_argument("--folder-url", default="Shared Documents", help="server-relative folder URL")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    folder = ctx.web.get_folder_by_server_relative_url(args.folder_url).select(["Exists"]).get().execute_query()
    print(f"Folder '{args.folder_url}' {'is found' if folder.exists else 'not found'}")


if __name__ == "__main__":
    main()
