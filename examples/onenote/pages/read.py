"""
Download a OneNote page's HTML.

``get_content()`` returns the page's HTML — the same markup OneNote renders,
including the ``name:`` references to its embedded parts. Use it to archive a
page, feed its text to another tool, or diff it over time. Because there is no
"list every page" call, this script walks the notebook's sections to find a page
(optionally the one named by ``--title``) and writes the HTML to a temp file.

The content is fetched from the top-level ``/onenote/pages/{id}`` resource: the
nested section path that a page is listed under is not accepted by the content
endpoint.

    python read.py
    python read.py --title "Project status" --out /tmp/page.html

Requires delegated permission ``Notes.Read`` (``Notes.ReadWrite`` also works).

https://learn.microsoft.com/en-us/graph/api/page-get
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.odata.literals import escape_odata_string
from tests.settings import client_id, password, tenant, username

NOTES_READ = ("Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All")


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_notebook(client: GraphClient, name: str | None):
    if name:
        notebook = client.me.onenote.notebooks.first_or_none(
            f"displayName eq '{escape_odata_string(name)}'"
        ).execute_query()
        if not notebook.is_loaded:
            raise SystemExit(f"No notebook named {name!r}.")
        return notebook
    notebook = next((nb for nb in client.me.onenote.notebooks.get().execute_query() if nb.is_default), None)
    if notebook is None:
        raise SystemExit("You have no default notebook; pass --notebook <name>.")
    return notebook


def _iter_sections(container):
    """Yield the sections in a notebook or section group, recursing into nested groups."""
    yield from container.sections.get().execute_query()
    for group in container.section_groups.get().execute_query():
        yield from _iter_sections(group)


def _find_page(client: GraphClient, notebook_name: str | None, title: str | None):
    notebook = _resolve_notebook(client, notebook_name)
    for section in _iter_sections(notebook):
        pages = section.pages.top(50).select(["id", "title", "lastModifiedDateTime"]).get().execute_query()
        for page in pages:
            if title is None or page.title == title:
                return notebook, section, page
    wanted = f" titled {title!r}" if title else ""
    raise SystemExit(f"No page{wanted} found in {notebook.display_name!r}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a OneNote page's HTML content")
    parser.add_argument("--notebook", help="notebook to search (default: your default notebook)")
    parser.add_argument("--title", help="page title to find (default: the first page)")
    parser.add_argument("--out", help="output file (default: onenote_page.html in the temp directory)")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_READ)
    _notebook, section, found = _find_page(client, args.notebook, args.title)
    if not found.id:
        raise SystemExit("The page has no id; cannot download its content.")

    # Address the page from the top-level collection before asking for its content.
    page = client.me.onenote.pages[found.id]
    content = page.get_content().execute_query().value
    out = Path(args.out) if args.out else Path(tempfile.gettempdir()) / "onenote_page.html"
    out.write_bytes(content)

    print(f"Page {found.title or '(untitled)'!r} in {section.display_name!r}")
    print(f"  {len(content):,} bytes of HTML written to {out}")


if __name__ == "__main__":
    main()
