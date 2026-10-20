"""
Export a contact folder as a portable vCard tree.

Each contact lands as ``<folder>/<name>_<iddigest>.vcf`` plus a JSON sidecar
carrying what a vCard cannot (the Graph id, the office fields, the address
components, categories, the created/modified times), and the run ends with a
``manifest.jsonl`` index. ``.vcf`` opens in Outlook, Google Contacts and iOS
Contacts, so the export is both an archive and the input for an import.

The job is the same ``MigrationJob`` the SharePoint, mail and calendar adapters
use, so it plans, resumes and verifies: a re-run skips what is already on disk,
and ``verify()`` compares each ``.vcf`` checksum against the document rendered
from the source contact.

Requires delegated permission ``Contacts.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-contactfolders
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob, MigrationOptions
from office365.migration.outlook import ContactExportOptions, ContactSource, VcfExportTarget
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Export a contact folder to a vCard tree")
    parser.add_argument("--folder", default=None, help="contact folder id (default: the user's contacts)")
    parser.add_argument("--output", default=None, help="output directory (default: temp dir)")
    parser.add_argument("--root-name", default=None, help="top folder name (default: the folder's display name)")
    parser.add_argument("--no-subfolders", action="store_true", help="only this folder, not its children")
    parser.add_argument("--preserve-timestamps", action="store_true", help="stamp each .vcf with its modified time")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = (
        client.me.contact_folders[args.folder].get().execute_query()
        if args.folder
        else client.me.contact_folders["contacts"].get().execute_query()
    )
    output = Path(args.output or tempfile.mkdtemp(prefix="contacts-export-"))

    options = ContactExportOptions(
        root_name=args.root_name,
        include_subfolders=not args.no_subfolders,
    )
    job = MigrationJob(
        ContactSource(folder, options),
        VcfExportTarget(output),
        options=MigrationOptions(preserve_timestamps=args.preserve_timestamps),
    )

    job.plan()
    print(f"Planned {len(job.manifest)} contacts from {folder.display_name}")
    stats = job.run()
    print(stats.summary())
    print(job.verify().summary())
    print(f"Export written to {output}")


if __name__ == "__main__":
    main()
