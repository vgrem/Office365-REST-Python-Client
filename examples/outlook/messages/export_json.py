"""
Export messages from a folder to a JSON file via the data pipeline
(``export_to(..., format="json")``).

A backup / interchange format — one JSON array of records that can be
version-controlled or re-imported elsewhere.

Requires delegated permission ``Mail.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-messages
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username

COLUMNS = ["subject", "from", "toRecipients", "sentDateTime", "receivedDateTime", "hasAttachments"]


def main():
    parser = argparse.ArgumentParser(description="Export messages to JSON via the data pipeline")
    parser.add_argument("--folder", default="inbox", help="folder path or id")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "mail_export.json"), help="output JSON file"
    )
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    messages = client.me.mail_folders[args.folder].messages.get_all().select(COLUMNS)

    with open(args.output, "w", encoding="utf-8") as f:
        messages.export_to(f, format="json").execute_query()

    print(f"Exported messages to {args.output}")


if __name__ == "__main__":
    main()
