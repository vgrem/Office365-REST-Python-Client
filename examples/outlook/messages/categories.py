"""
Manage master categories (the colour labels used on messages and events).

A master category (``outlookCategory``) is tenant/user-level: rules and items
reference it by name, so create it once and reuse. Categories come in a fixed set
of colours; the ``preset`` colour is chosen by the server.

Requires delegated permission ``MailboxSettings.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/resources/outlookcategory
https://learn.microsoft.com/en-us/graph/api/outlookuser-post-mastercategories
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and list master categories")
    parser.add_argument("--keep", action="store_true", help="keep the created category")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    categories = client.me.outlook.master_categories

    name = create_unique_name("Project")
    category = categories.add(display_name=name, color="preset0").execute_query()
    print(f"Created category {category.display_name!r}  colour={category.color}")

    current = categories.get().execute_query()
    print(f"\nCategories ({len(current)}):")
    for item in current:
        marker = "  <- new" if item.id == category.id else ""
        print(f"  {item.display_name:30}  {item.color or '-':10}{marker}")

    if not args.keep:
        category.delete_object().execute_query()
        print(f"\nDeleted {name!r}.")


if __name__ == "__main__":
    main()
