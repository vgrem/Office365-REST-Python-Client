"""
Import a portable EML tree into a mailbox folder, recreating the folder chain.

The tree is the one `examples/outlook/migration/export` writes: ``.eml`` files plus
their JSON sidecars. The import is the same ``MigrationJob``, so it plans, resumes
and verifies — a re-run skips what the mailbox already has, and ``verify()`` compares
each message's semantic digest rather than its bytes (Exchange re-serializes MIME).

What survives the round trip: the message itself (headers, bodies, attachments), the
folder chain and the names the user knows, and — replayed with one extra PATCH —
read state, Outlook categories and importance. What does not: the message arrives as
a draft, and its received date is the import time (the original date is preserved in
the ``Date`` header, exposed by Graph as ``sentDateTime``).

Requires delegated permission ``Mail.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/user-post-messages
"""

import argparse
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import EmlTreeSource, MailboxTarget, MailImportOptions
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Import an EML tree into a mailbox folder")
    parser.add_argument("--source", required=True, help="directory of exported .eml files")
    parser.add_argument("--folder", default="inbox", help="well-known name or folder id of the import root")
    parser.add_argument("--root-name", default=None, help="create the tree under this child folder instead")
    parser.add_argument("--no-read-state", action="store_true", help="leave every imported message marked read")
    parser.add_argument("--no-categories", action="store_true", help="do not replay Outlook categories")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = client.me.mail_folders[args.folder].get().execute_query()
    source = Path(args.source)

    options = MailImportOptions(
        restore_read_state=not args.no_read_state,
        restore_categories=not args.no_categories,
        root_name=args.root_name,
    )
    job = MigrationJob(EmlTreeSource(source), MailboxTarget(folder, options))

    job.plan()
    print(f"Planned {len(job.manifest)} messages from {source}")
    stats = job.run()
    print(stats.summary())

    report = job.verify()
    print(report.summary())
    print(f"Imported into {folder.display_name}")


if __name__ == "__main__":
    main()
