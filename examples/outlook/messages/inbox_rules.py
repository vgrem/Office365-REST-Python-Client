"""
Create an inbox rule and manage message categories.

Two related bits of automation: **master categories** (the colour labels) and
**inbox rules** (server-side conditions → actions). Both are created with a
unique name and removed at the end, so the script is safe to re-run.

Requires delegated permission ``Mail.ReadWrite`` and ``MailboxSettings.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/mailfolder-post-messagerules
https://learn.microsoft.com/en-us/graph/api/outlookuser-post-mastercategories
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.outlook.mail.importance import Importance
from office365.outlook.mail.messages.rules.actions import MessageRuleActions
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an inbox rule and a category")
    parser.add_argument("--keep", action="store_true", help="keep the created rule and category")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    # 1. A master category (the colour used to tag messages).
    category_name = create_unique_name("Urgent")
    category = client.me.outlook.master_categories.add(display_name=category_name, color="preset5").execute_query()
    print(f"Category created: {category.display_name}")

    # 2. An inbox rule: flag high-importance mail, no forwarding.
    actions = MessageRuleActions(markImportance=Importance.high, stopProcessingRules=False)
    rule = client.me.mail_folders["inbox"].message_rules.add(create_unique_name("SDK Rule"), 2, actions).execute_query()
    print(f"Rule created: {rule.display_name} (sequence: {rule.sequence})")

    rules = client.me.mail_folders["inbox"].message_rules.get().execute_query()
    print(f"\nInbox rules ({len(rules)}):")
    for item in rules:
        print(f"  {item.display_name}  enabled={item.is_enabled}  sequence={item.sequence}")

    if not args.keep:
        rule.delete_object().execute_query()
        category.delete_object().execute_query()
        print("\nCleaned up the rule and category.")


if __name__ == "__main__":
    main()
