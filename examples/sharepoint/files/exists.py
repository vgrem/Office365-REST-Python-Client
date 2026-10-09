"""
Check whether a file exists on a SharePoint site (without raising on a miss).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Check whether a file exists")
    parser.add_argument("--file-url", default="/Shared Documents/Financial Sample.xlsx", help="server-relative file URL")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    exists = ctx.web.get_file_by_server_relative_url(args.file_url).get_exists().execute_query().value
    print(f"File '{args.file_url}' {'exists' if exists else 'not found'}.")


if __name__ == "__main__":
    main()
