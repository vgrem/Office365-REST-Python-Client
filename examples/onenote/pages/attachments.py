"""
Create a OneNote page with an inline image and file attachments.

OneNote embeds non-HTML content by reference: the page HTML points at a named
part (``<img src="name:imageBlock1">`` and ``<object data="name:fileBlock1">``)
and the matching multipart parts carry the bytes. The library builds that
multipart body for you — pass the HTML as the presentation part and a mapping
from the part name used in the HTML to the file.

``data/Sample.html`` already references ``imageBlock1``, ``fileBlock1`` and
``fileBlock2``, so the mapping below is what ties the page to its parts. The page
is created in a dedicated ``SDK OneNote Tour`` notebook and deleted again unless
``--keep``.

    python attachments.py
    python attachments.py --keep

Requires delegated permission ``Notes.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/onenote-create-page
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, username

NOTES_WRITE = ("Notes.Create", "Notes.ReadWrite", "Notes.ReadWrite.All")
EXAMPLE_NOTEBOOK = "SDK OneNote Tour"
EXAMPLE_SECTION = "SDK Examples"

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


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
    parser = argparse.ArgumentParser(description="Create a OneNote page with an image and file attachments")
    parser.add_argument("--keep", action="store_true", help="keep the page instead of deleting it")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_WRITE)
    section = _ensure_section(client)

    # Part name in the HTML -> file on disk. The files' names drive their MIME
    # types (an image/jpeg part for the <img>, application/pdf, docx, ...).
    with (DATA_DIR / "Sample.html").open("rb") as html, (DATA_DIR / "office-logo-icon.jpg").open("rb") as image, (
        DATA_DIR / "Sample.pdf"
    ).open("rb") as pdf, (DATA_DIR / "SharePoint User Guide.docx").open("rb") as word:
        attachments = {"imageBlock1": image, "fileBlock1": pdf, "fileBlock2": word}
        page = section.pages.add(presentation_file=html, attachment_files=attachments).execute_query()

    print(f"Created page {page.title or '(untitled)'!r} in {section.display_name!r}")
    print(f"  {page.links.oneNoteWebUrl.href}")

    if not args.keep:
        _delete_page(page)
        print("Deleted the page again (pass --keep to keep it).")


if __name__ == "__main__":
    main()
