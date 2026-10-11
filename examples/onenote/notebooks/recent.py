"""
Your recently accessed OneNote notebooks.

``getRecentNotebooks`` builds a "jump back in" list without walking the
hierarchy: it returns the notebooks the signed-in user opened most recently,
newest first. It is a function on the notebooks collection, so it runs with
``execute_query()`` and the result is in ``.value``.

    python recent.py
    python recent.py --limit 10

Requires delegated permission ``Notes.Read``.

https://learn.microsoft.com/en-us/graph/api/notebook-getrecentnotebooks
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

NOTES_READ = ("Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All")


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def main() -> None:
    parser = argparse.ArgumentParser(description="List your recently accessed notebooks")
    parser.add_argument("--limit", type=int, default=10, help="how many notebooks to print (default: 10)")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_READ)
    result = client.me.onenote.notebooks.get_recent_notebooks(True).execute_query()

    recent = list(result.value)
    print(f"{len(recent)} recently accessed notebook(s):\n")
    for item in recent[: args.limit]:
        print(f"  {item.displayName or '(untitled)'}")
        print(f"    last opened: {item.lastAccessedTime}   source: {item.sourceService}")
        print(f"    {item.links.oneNoteWebUrl.href}")


if __name__ == "__main__":
    main()
