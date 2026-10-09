"""
Retrieve filesystem timestamps and authorship for a file.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Retrieve file system metadata")
    parser.add_argument("--file-url", default="SitePages/Home.aspx", help="server-relative file URL")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    file = ctx.web.get_file_by_server_relative_url(args.file_url).expand(["Author", "ModifiedBy"]).get().execute_query()

    print(f"Author:        {file.author}")
    print(f"Modified by:   {file.modified_by}")
    print(f"Created:       {file.time_created}")
    print(f"Last modified: {file.time_last_modified}")


if __name__ == "__main__":
    main()
