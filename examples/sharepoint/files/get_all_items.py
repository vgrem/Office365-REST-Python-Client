"""
Enumerate files and folders within a document library.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/file-operations
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.system_object_type import FileSystemObjectType
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Enumerate files and folders within the default document library")
    parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    items = (
        ctx.web.default_document_library()
        .items.select(["FileSystemObjectType"])
        .expand(["File", "Folder"])
        .get_all()
        .execute_query()
    )
    for item in items:
        if item.file_system_object_type == FileSystemObjectType.Folder:
            print(f"Folder  {item.folder.server_relative_url}")
        else:
            print(f"File    {item.file.server_relative_url}")
    print(f"\n{len(items)} item(s)")


if __name__ == "__main__":
    main()
