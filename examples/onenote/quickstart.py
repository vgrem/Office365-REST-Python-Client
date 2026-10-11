"""
OneNote quickstart — a read-only map of your notebooks, sections and pages.

OneNote is a four-level hierarchy (notebook → section group → section → page)
and, unlike Mail or Calendar, there is no single call that returns every page.
The way in is per notebook, then per section. This script reads the top of that
tree and prints what it finds — a good first look before the rest of the folder.

    python quickstart.py
    python quickstart.py --notebook "Project X" --limit 5

Requires delegated permission ``Notes.Read`` (``Notes.ReadWrite`` to change
anything).

https://learn.microsoft.com/en-us/graph/api/resources/onenote-api-overview
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

NOTES_READ = ("Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All")


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _pick_notebook(notebooks: list, name: str | None):
    """One named ``name``, else the default notebook, else the first one (if any)."""
    if name:
        return next((nb for nb in notebooks if nb.display_name == name), None)
    return next((nb for nb in notebooks if nb.is_default), notebooks[0] if notebooks else None)


def main() -> None:
    parser = argparse.ArgumentParser(description="A read-only look at your OneNote notebooks")
    parser.add_argument("--notebook", help="notebook to inspect (default: your default notebook)")
    parser.add_argument("--limit", type=int, default=5, help="how many sections and pages to print (default: 5)")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_READ)

    notebooks = list(client.me.onenote.notebooks.get().execute_query())
    print(f"You have {len(notebooks)} notebook(s).\n")

    notebook = _pick_notebook(notebooks, args.notebook)
    if notebook is None:
        print(f"No notebook named {args.notebook!r}.")
        return

    sections = list(notebook.sections.get().execute_query())
    groups = notebook.section_groups.get().execute_query()
    print(f"{notebook.display_name} — {len(sections)} section(s), {len(groups)} section group(s)")
    for section in sections[: args.limit]:
        pages = list(section.pages.top(args.limit).select(["title", "lastModifiedDateTime"]).get().execute_query())
        titles = ", ".join(page.title or "(untitled)" for page in pages) or "no pages"
        print(f"  {section.display_name}: {titles}")

    print(f"\nWeb: {notebook.links.oneNoteWebUrl.href}")


if __name__ == "__main__":
    main()
