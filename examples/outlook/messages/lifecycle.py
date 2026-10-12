"""
Message lifecycle: reply, forward, move, and copy messages.

Covers the most common post-receive operations:
  - Reply to sender (with modified body)
  - Forward to another recipient
  - Move to a different folder
  - Copy to a different folder

The pattern: create a draft → optionally edit → save or send.

Requires delegated permission ``Mail.ReadWrite`` and ``Mail.Send``.

https://learn.microsoft.com/en-us/graph/api/message-createreply
https://learn.microsoft.com/en-us/graph/api/message-forward
https://learn.microsoft.com/en-us/graph/api/message-move
https://learn.microsoft.com/en-us/graph/api/message-copy
"""

import sys
import time

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, password, tenant, user_principal, username


def get_latest_inbox_message(client: GraphClient):
    """Return the most recent message in the inbox, or None."""
    messages = client.me.mail_folders["inbox"].messages.top(1).get().execute_query()
    return messages[0] if len(messages) > 0 else None


def main():
    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)

    # -- Step 1: pick a message to work with --
    message = get_latest_inbox_message(client)
    if message is None:
        sys.exit("No messages in inbox.")

    # Load subject and body for display
    message.select(["subject", "body"]).execute_query()
    print(f'Source message: "{message.subject}"\n')

    # -- Step 2: reply --
    draft = message.create_reply().execute_query()
    # Draft body is auto-populated; append a line
    body = draft.body.get_property("content", "")
    draft.set_property("body", {"contentType": "Text", "content": body + "\n\n---\nSent via Microsoft Graph SDK"})
    draft.update().execute_query()
    draft.send().execute_query()
    print("✓ Reply sent (with appended signature).")

    # -- Step 3: forward --
    forward_to = user_principal
    message.forward(to_recipients=[forward_to], comment="FYI — see below.").execute_query()
    print(f"✓ Forwarded to {forward_to}.")

    # -- Step 4: move to a subfolder --
    # Ensure a subfolder exists
    inbox = client.me.mail_folders["inbox"].get().execute_query()
    archive_folder = inbox.child_folders.ensure("Archive").execute_query()

    moved = message.move(archive_folder.id).execute_query()
    print(f"✓ Moved to '{archive_folder.display_name}' (new id: {moved.id})")

    # -- Step 5: copy back to inbox --
    # A move is eventually consistent, so the new id may 404 for a moment.
    inbox = client.me.mail_folders["inbox"].get().execute_query()
    copy_source = client.me.messages[moved.id]
    for _ in range(5):
        try:
            copy_source.get().execute_query()
            break
        except ClientRequestException:
            time.sleep(2)
    copy_source.copy(inbox.id).execute_query()
    print("✓ Copied back to Inbox.")


if __name__ == "__main__":
    main()
