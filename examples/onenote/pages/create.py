"""
Create a rich OneNote page from input HTML.

A page is submitted as HTML: headings, paragraphs, bullet and numbered lists,
tables and styled spans all translate into OneNote content. The page goes into a
section, so this script finds (or creates) a ``SDK Examples`` section in a
dedicated ``SDK OneNote Tour`` notebook, creates the page there, then deletes it
again so the notebook is left as it was — pass ``--keep`` to keep the page.

    python create.py
    python create.py --keep

Requires delegated permission ``Notes.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/onenote-create-page
https://learn.microsoft.com/en-us/graph/onenote-input-output-html
"""

from __future__ import annotations

import argparse
import time

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username

NOTES_WRITE = ("Notes.Create", "Notes.ReadWrite", "Notes.ReadWrite.All")
EXAMPLE_NOTEBOOK = "SDK OneNote Tour"
EXAMPLE_SECTION = "SDK Examples"

PAGE_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Project status</title>
    <style>
        h1 { color: #0078d4; }
        .done { background: #dff6dd; }
        .wip { background: #fff3ce; }
    </style>
</head>
<body>
    <h1>Project status</h1>
    <p>Generated through the <strong>Microsoft Graph API</strong>.</p>

    <h2>Team</h2>
    <ul>
        <li><b>Alice</b> — engineering lead</li>
        <li><b>Bob</b> — product manager</li>
        <li><b>Carol</b> — designer</li>
    </ul>

    <h2>Milestones</h2>
    <ol>
        <li>Design review <span class="done">done</span></li>
        <li>API integration <span class="wip">in progress</span></li>
        <li>User testing</li>
    </ol>

    <h2>Budget</h2>
    <table>
        <thead>
            <tr><th>Category</th><th>Budget</th><th>Spent</th></tr>
        </thead>
        <tbody>
            <tr><td>Engineering</td><td>$50,000</td><td>$32,000</td></tr>
            <tr><td>Design</td><td>$15,000</td><td>$8,500</td></tr>
            <tr><td>Operations</td><td>$10,000</td><td>$9,200</td></tr>
        </tbody>
    </table>
</body>
</html>"""


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _ensure_section(client: GraphClient):
    """Find, or create, the dedicated ``SDK Examples`` section of the tour notebook."""
    notebooks = client.me.onenote.notebooks
    notebook = notebooks.find_by_display_name(EXAMPLE_NOTEBOOK).execute_query()
    if not notebook.is_loaded:
        notebook = notebooks.add(EXAMPLE_NOTEBOOK).execute_query()
        print(f"Created notebook {EXAMPLE_NOTEBOOK!r} (Graph cannot delete notebooks).")
    section = notebook.sections.find_by_display_name(EXAMPLE_SECTION).execute_query()
    if section.is_loaded:
        return section
    return notebook.sections.add(displayName=EXAMPLE_SECTION).execute_query()


def _delete_page(page) -> None:
    """Delete a page, retrying briefly: OneNote needs a moment to settle a just-created page."""
    retries = 2
    for attempt in range(retries + 1):
        try:
            page.delete_object().execute_query()
            return
        except ClientRequestException as ex:
            if attempt == retries or ex.code != "20102":
                raise
            time.sleep(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a rich OneNote page from HTML")
    parser.add_argument("--keep", action="store_true", help="keep the page instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_WRITE)
    section = _ensure_section(client)

    page = section.pages.add(presentation_file=PAGE_HTML).execute_query()
    print(f"Created page {page.title or '(untitled)'!r} in {section.display_name!r}")
    print(f"  {page.links.oneNoteWebUrl.href}")

    if not args.keep:
        _delete_page(page)
        print("Deleted the page again (pass --keep to keep it).")


if __name__ == "__main__":
    main()
