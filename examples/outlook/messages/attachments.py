"""
Add, list and download attachments on a message.

An attachment is a child of a message: a **fileAttachment** (bytes) or an
**itemAttachment** (a whole message/event). For a *new* draft the attachment rides
along with the message ``POST``; for an *existing* message it is uploaded to the
message's ``attachments`` collection — ``add_file_attachment`` does either.

Requires delegated permission ``Mail.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/message-post-attachments
https://learn.microsoft.com/en-us/graph/api/resources/fileattachment
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.settings import client_id, password, tenant, user_principal, username


def main() -> None:
    parser = argparse.ArgumentParser(description="Attach a file to a draft message")
    parser.add_argument("--keep", action="store_true", help="keep the draft")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    # Build the draft, attach the file, then create it in one round-trip.
    draft = client.me.messages.add(
        subject=create_unique_name("Attachment demo"),
        body="See the attached file.",
        to_recipients=[user_principal],
    )
    draft.add_file_attachment("note.txt", b"Hello from an attachment\n", "text/plain")
    draft.execute_query()
    print(f"Draft: {draft.subject!r}  id={draft.id}")

    attachments = draft.attachments.get().execute_query()
    print(f"Attachments ({len(attachments)}):")
    for attachment in attachments:
        print(f"  {attachment.name}  type={attachment.content_type}  size={attachment.size}")

    if attachments:
        content = attachments[0].get_content().execute_query().value
        print(f"  downloaded {len(content)} bytes back")

    if not args.keep:
        draft.delete_object().execute_query()
        print("Draft deleted.")


if __name__ == "__main__":
    main()
