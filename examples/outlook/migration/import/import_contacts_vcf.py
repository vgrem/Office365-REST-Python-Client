"""
Import a portable vCard tree into a contact folder, recreating folders and contacts.

The tree is the one `examples/outlook/migration/export` writes: ``.vcf`` files plus
their JSON sidecars. The sidecar is mandatory here — a vCard cannot carry the office
fields, the address components or the categories without a lossy mapping — so a
``.vcf`` without its ``.json`` raises instead of importing a thinner contact. The
import is the same ``MigrationJob``, so it plans, resumes and verifies: a re-run skips
what the folder already has, and ``verify()`` compares a digest of the restorable
fields rather than the ``.vcf`` bytes (Exchange normalises a birthday and fills in a
missing email name).

What survives the round trip: every office field, both addresses, the phones, the
child folders, the categories and the notes. What does not: the photo, and the
created/modified times Exchange assigns itself.

Requires delegated permission ``Contacts.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/user-post-contacts
"""

import argparse
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import ContactImportOptions, ContactTarget, VcfTreeSource
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Import a vCard tree into a contact folder")
    parser.add_argument("--source", required=True, help="directory of exported .vcf files")
    parser.add_argument("--folder", default=None, help="contact folder id (default: the user's contacts)")
    parser.add_argument("--no-categories", action="store_true", help="do not restore Outlook categories")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    folder = (
        client.me.contact_folders[args.folder].get().execute_query()
        if args.folder
        else client.me.contact_folders["contacts"].get().execute_query()
    )
    source = Path(args.source)

    # One options object, shared by both adapters: the verification digest counts
    # categories only when the options say the import restores them.
    options = ContactImportOptions(restore_categories=not args.no_categories)
    job = MigrationJob(VcfTreeSource(source, options), ContactTarget(folder, options))

    job.plan()
    print(f"Planned {len(job.manifest)} contacts from {source}")
    stats = job.run()
    print(stats.summary())

    report = job.verify()
    print(report.summary())
    # Adapter warnings (a dropped category, an unfaithful field) are collected on the
    # target, the same convention the SharePoint adapters use.
    for warning in getattr(job.target, "warnings", None) or []:
        print(f"warning: {warning}")
    print(f"Imported into {folder.display_name}")


if __name__ == "__main__":
    main()
