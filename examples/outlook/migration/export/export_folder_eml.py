"""
Export a mail folder (with its subfolders) as a portable EML tree.

Each message lands as ``<folder>/<date>_<subject>_<id>.eml`` plus a JSON sidecar
carrying what MIME cannot (Graph ids, read state, categories, conversation), and
the run ends with a ``manifest.jsonl`` index which is one JSON record per line.
The job is the same ``MigrationJob`` the SharePoint adapters use, so it plans,
resumes, and verifies: a re-run skips what is already on disk, and ``verify()``
compares each exported file's checksum against the source message.

``.eml`` is the interchange format every client opens and every IMAP server
accepts as an ``APPEND``, so the export is both a backup and the input for an
import.

Requires delegated permission ``Mail.Read`` (the walker reads folders, messages,
and the MIME body).

https://learn.microsoft.com/en-us/graph/api/user-list-messages
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob, MigrationOptions
from office365.migration.outlook import MailExportOptions, MailExportTarget, MailFolderSource
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Export a mail folder to an EML tree")
    parser.add_argument("--folder", default="inbox", help="well-known name or folder id")
    parser.add_argument("--output", default=None, help="output directory (default: temp dir)")
    parser.add_argument("--flat", action="store_true", help="do not descend into subfolders")
    parser.add_argument("--no-drafts", action="store_true", help="skip drafts")
    parser.add_argument("--preserve-timestamps", action="store_true", help="stamp each .eml with its modified time")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = client.me.mail_folders[args.folder].get().execute_query()
    output = Path(args.output or tempfile.mkdtemp(prefix="mail-export-"))

    options = MailExportOptions(include_subfolders=not args.flat, include_drafts=not args.no_drafts)
    job = MigrationJob(
        MailFolderSource(folder, options),
        MailExportTarget(output),
        options=MigrationOptions(preserve_timestamps=args.preserve_timestamps),
    )

    job.plan()
    print(f"Planned {len(job.manifest)} messages from {folder.display_name}")
    stats = job.run()
    print(f"{stats.summary()}")

    report = job.verify()
    print(report.summary())
    print(f"Export written to {output}")


if __name__ == "__main__":
    main()
