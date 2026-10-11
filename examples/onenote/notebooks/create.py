"""
Create a OneNote notebook.

A notebook is the top of the OneNote hierarchy and the only resource you create
without a parent. The name must be unique across the signed-in user's notebooks;
without ``--name`` this script derives one from the current time so reruns never
collide.

    python create.py
    python create.py --name "Project X"

Requires delegated permission ``Notes.ReadWrite`` (``Notes.Create`` also works).

Microsoft Graph has no delete-notebook operation — remove the notebook from
OneNote when you are done with it.

https://learn.microsoft.com/en-us/graph/api/onenote-post-notebooks
"""

from __future__ import annotations

import argparse
from datetime import datetime

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

NOTES_WRITE = ("Notes.Create", "Notes.ReadWrite", "Notes.ReadWrite.All")


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a OneNote notebook")
    parser.add_argument("--name", help="notebook name (default: a timestamped 'SDK OneNote <time>')")
    args = parser.parse_args()

    name = args.name or f"SDK OneNote {datetime.now():%Y%m%d-%H%M%S}"
    client = _client().require_delegated_permission(*NOTES_WRITE)

    notebook = client.me.onenote.notebooks.add(name).execute_query()
    print(f"Created notebook: {notebook.display_name}")
    print(f"  id:  {notebook.id}")
    print(f"  web: {notebook.links.oneNoteWebUrl.href}")
    print("\nGraph cannot delete notebooks — remove it from OneNote when you are done.")


if __name__ == "__main__":
    main()
