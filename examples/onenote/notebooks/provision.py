"""
Provision a OneNote notebook from a template.

Notebooks are the unit of standardization: create one notebook and lay down the
same sections and opening pages every time — handy for onboarding a project, a
team or a training course. This script is **idempotent**: an existing section is
reused by name, and a starter page is only added when its section is still
empty, so running it again changes nothing.

    python provision.py
    python provision.py --notebook "Project X"

Requires delegated permission ``Notes.ReadWrite`` (``Notes.Create`` to create a
missing notebook).

https://learn.microsoft.com/en-us/graph/api/onenote-post-notebooks
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

NOTES_WRITE = ("Notes.Create", "Notes.ReadWrite", "Notes.ReadWrite.All")
DEFAULT_NOTEBOOK = "SDK OneNote Tour"

#: section name → opening page body (the page title is the section name)
TEMPLATE: dict[str, str] = {
    "Meeting Notes": "<p>Weekly sync notes go here.</p>",
    "Project Plan": "<p>Timeline, milestones and deliverables.</p>",
    "Decisions": "<p>Architecture and design decisions, with the rationale.</p>",
    "Resources": "<p>Links to the docs, tools and dashboards we rely on.</p>",
}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_notebook(client: GraphClient, name: str):
    """Return ``(notebook, created)`` — create ``name`` when it does not exist yet."""
    notebooks = client.me.onenote.notebooks
    notebook = notebooks.find_by_display_name(name).execute_query()
    if notebook.is_loaded:
        return notebook, False
    return notebooks.add(name).execute_query(), True


def _starter_page(section_name: str, body: str) -> str:
    return (
        f"<!DOCTYPE html><html><head><title>{section_name}</title></head>"
        f"<body><h1>{section_name}</h1>{body}</body></html>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision a notebook from a template")
    parser.add_argument("--notebook", default=DEFAULT_NOTEBOOK, help="target notebook, created if missing")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_WRITE)
    notebook, created = _resolve_notebook(client, args.notebook)
    print(f"Notebook {notebook.display_name!r} ({'created' if created else 'reused'})")

    for section_name, body in TEMPLATE.items():
        section = notebook.sections.find_by_display_name(section_name).execute_query()
        if section.is_loaded:
            print(f"  section {section.display_name!r} (exists)")
        else:
            section = notebook.sections.add(displayName=section_name).execute_query()
            print(f"  section {section.display_name!r} (created)")

        pages = list(section.pages.top(1).get().execute_query())
        if pages:
            print(f"    page {pages[0].title or '(untitled)'!r} (exists)")
        else:
            page = section.pages.add(presentation_file=_starter_page(section_name, body)).execute_query()
            print(f"    page {page.title or '(untitled)'!r} (created)")

    print(f"\nWeb: {notebook.links.oneNoteWebUrl.href}")


if __name__ == "__main__":
    main()
