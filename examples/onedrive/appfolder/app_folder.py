"""
Store app-specific data in a reserved application folder.

An app that only needs to keep *its own* files shouldn't ask for the user's whole
drive. OneDrive reserves a private ``approot`` special folder for exactly this;
with the ``Files.ReadWrite.AppFolder`` scope the app sees only that folder, and
the user sees it under *Apps*.

Requires the delegated ``Files.ReadWrite.AppFolder`` scope.

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/special-folders-appfolder
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Use an app's private folder inside a user's drive")
    parser.add_argument("--keep", action="store_true", help="keep the sample file")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    # `special` resolves canonical folders by name; `approot` is this app's sandbox.
    app_folder = client.me.drive.special["approot"].get().execute_query()
    print(f"App folder: {app_folder.name}  ({app_folder.web_url})")

    item = app_folder.upload(f"{create_unique_name('state')}.json", b'{"enabled": true}\n').execute_query()
    print(f"Stored {item.name} ({item.size:,} bytes) — visible only to this app")

    if not args.keep:
        item.delete_object().execute_query()
        print("Removed.")


if __name__ == "__main__":
    main()
