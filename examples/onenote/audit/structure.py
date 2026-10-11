"""
Audit the OneNote hierarchy — notebooks, section groups, sections and pages.

Content discovery and migration planning need the whole tree, and OneNote is the
product where that means walking it yourself: notebooks contain section groups
(which nest), section groups contain sections, and sections contain pages. This
script walks a bounded slice of that tree — the first ``--limit`` notebooks and
``--pages`` pages per section — printing it and optionally dumping it as JSON.

    python structure.py
    python structure.py --limit 5 --pages 20
    python structure.py --json

Requires delegated permission ``Notes.Read``.

https://learn.microsoft.com/en-us/graph/api/onenote-list-notebooks
https://learn.microsoft.com/en-us/graph/api/onenote-list-pages
"""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

NOTES_READ = ("Notes.Read", "Notes.Read.All", "Notes.ReadWrite", "Notes.ReadWrite.All")


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _iso(value) -> str | None:
    return value.isoformat() if isinstance(value, datetime) else value


def _section_node(section, page_limit: int) -> dict:
    pages = section.pages.top(page_limit).select(["id", "title", "lastModifiedDateTime"]).get().execute_query()
    return {
        "name": section.display_name,
        "pages": [
            {"id": page.id, "title": page.title, "modified": _iso(page.last_modified_date_time)} for page in pages
        ],
    }


def _group_node(group, page_limit: int) -> dict:
    return {
        "name": group.display_name,
        "sections": [_section_node(s, page_limit) for s in group.sections.get().execute_query()],
        "section_groups": [_group_node(child, page_limit) for child in group.section_groups.get().execute_query()],
    }


def _notebook_node(notebook, page_limit: int) -> dict:
    return {
        "name": notebook.display_name,
        "default": bool(notebook.is_default),
        "sections": [_section_node(s, page_limit) for s in notebook.sections.get().execute_query()],
        "section_groups": [_group_node(g, page_limit) for g in notebook.section_groups.get().execute_query()],
    }


def _print_section(section: dict, depth: int) -> None:
    pad = "  " * depth
    print(f"{pad}▸ {section['name'] or '(untitled)'}  ({len(section['pages'])} page(s))")
    for page in section["pages"]:
        print(f"{pad}   • {page['title'] or '(untitled)'}  [{page['modified']}]")


def _print_group(group: dict, depth: int) -> None:
    pad = "  " * depth
    print(f"{pad}▸ {group['name'] or '(untitled)'}  (section group)")
    for section in group["sections"]:
        _print_section(section, depth + 1)
    for child in group["section_groups"]:
        _print_group(child, depth + 1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit your OneNote notebook hierarchy")
    parser.add_argument("--limit", type=int, default=10, help="how many notebooks to walk (default: 10)")
    parser.add_argument("--pages", type=int, default=10, help="how many pages to read per section (default: 10)")
    parser.add_argument("--notebook", help="only walk the notebook with this name")
    parser.add_argument("--json", action="store_true", help="also write the tree as JSON to the temp directory")
    args = parser.parse_args()

    client = _client().require_delegated_permission(*NOTES_READ)
    notebooks = list(client.me.onenote.notebooks.get().execute_query())
    if args.notebook:
        notebooks = [nb for nb in notebooks if nb.display_name == args.notebook]
    notebooks = notebooks[: args.limit]

    tree = [_notebook_node(notebook, args.pages) for notebook in notebooks]
    print(f"{len(tree)} notebook(s):\n")
    for node in tree:
        suffix = " (default)" if node["default"] else ""
        print(f"{node['name'] or '(untitled)'}{suffix}")
        for section in node["sections"]:
            _print_section(section, 1)
        for group in node["section_groups"]:
            _print_group(group, 1)
        print()

    if args.json:
        out = Path(tempfile.gettempdir()) / "onenote_structure.json"
        out.write_text(json.dumps(tree, indent=2), encoding="utf-8")
        print(f"JSON written to {out}")


if __name__ == "__main__":
    main()
