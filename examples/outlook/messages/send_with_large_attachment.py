"""
Send a message with a large file attachment via an upload session.

Files larger than ~3 MB can't be attached inline — Graph wants an upload session,
and the library's ``upload_attachment`` handles it for you. The file path is
resolved relative to this script, so it runs from anywhere.

Requires delegated permission ``Mail.ReadWrite`` and ``Mail.Send``.

https://learn.microsoft.com/en-us/graph/api/attachment-createuploadsession
"""

from __future__ import annotations

import argparse
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, user_principal, username

DEFAULT_FILE = Path(__file__).resolve().parents[3] / "tests" / "data" / "big_buck_bunny.mp4"


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a message with a large attachment (upload session)")
    parser.add_argument("--path", default=str(DEFAULT_FILE), help="file to attach")
    parser.add_argument("--to", action="append", default=[], help="recipient (repeatable; default: the test user)")
    parser.add_argument("--send", action="store_true", help="actually send (otherwise build the draft only)")
    args = parser.parse_args()

    recipients = args.to or [user_principal]

    def on_progress(position: int) -> None:
        print(f"  {position:,} bytes uploaded")

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    message = client.me.messages.add(
        subject="Large attachment",
        body="See the attached file.",
        to_recipients=recipients,
    ).upload_attachment(args.path, on_progress)

    if args.send:
        message.send().execute_query()
        print(f"Sent {Path(args.path).name} to {', '.join(recipients)}")
    else:
        message.execute_query()
        print(f"Draft created with {Path(args.path).name}; re-run with --send to send it.")


if __name__ == "__main__":
    main()
