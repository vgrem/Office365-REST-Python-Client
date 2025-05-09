"""
Demonstrates how to download a files from SharePoint library
"""

import tempfile
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

doc_lib = ctx.web.lists.get_by_title("Documents")
items = (
    doc_lib.items.select(["FileSystemObjectType"])
    .select(["Id", "FileRef", "FileDirRef", "FileLeafRef"])
    .filter("FSObjType eq 0")
    .get_all()
    .execute_query()
)

download_root_path = Path(tempfile.mkdtemp())

for item in items:

    download_path = download_root_path / item.properties.get("FileDirRef").lstrip("/")
    download_path.mkdir(parents=True, exist_ok=True)

    download_file_path = download_path / item.properties.get("FileLeafRef")

    with open(download_file_path, "wb") as f:
        item.file.download(f).execute_query()
        print(f"File has been downloaded into {f.name}")
