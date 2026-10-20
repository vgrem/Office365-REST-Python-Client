"""
Migrate a document library to/from a local directory — bidirectional.

- Export (default): enumerate the library's files recursively and download
  them preserving the folder structure into a folder named after the library
  under the system temp dir (``--target`` overrides), and write the library's
  structure snapshot next to that folder as ``<target>.structure.json``. The two
  together are a self-describing bundle.
- Import (``--import DIR``): upload a local tree into the library with
  **parallel** workers (``--concurrency``), sharing a rate limiter that paces
  the fleet on ``Retry-After`` / ``X-SharePointHealthScore``. If
  ``DIR.structure.json`` exists (an export made it, or ``capture_structure.py``
  can produce one) its columns, content types, views and settings are replayed
  onto the target library first — a file uploaded into a bare library carries
  no column values of its own.

Requires: read access to the library (export), write access (import).
"""

from __future__ import annotations

import argparse
import os
import tempfile

from office365.migration import ConflictResolution, MigrationJob, MigrationOptions
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget
from office365.migration.sharepoint.adapters import SharePointLibrarySource, SharePointLibraryTarget
from office365.migration.sharepoint.structure import (
    capture_list_structure,
    load_list_structure,
    save_list_structure,
)
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username


def export_dir(library_url: str) -> str:
    name = library_url.strip("/").rsplit("/", 1)[-1] or "library"
    return os.path.join(tempfile.gettempdir(), f"lib-export-{name}")


def structure_path(content_dir: str) -> str:
    """The sidecar that sits *next to* the content directory, never inside it."""
    return f"{content_dir.rstrip('/')}.structure.json"


def main():
    parser = argparse.ArgumentParser(description="Migrate a document library to/from a local directory")
    parser.add_argument("--library-url", required=True, help="server-relative library URL")
    parser.add_argument("--import", dest="import_dir", help="local directory to import INTO the library")
    parser.add_argument("--target", default=None, help="local output directory (export only)")
    parser.add_argument("--structure", default=None, help="structure snapshot to replay (import only)")
    parser.add_argument("--concurrency", type=int, default=4, help="parallel upload workers (import only)")
    args = parser.parse_args()
    args.target = args.target or export_dir(args.library_url)

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    # Load it: the parallel upload path reads ``server_relative_url`` off the folder.
    folder = ctx.web.get_folder_by_server_relative_url(args.library_url).get().execute_query()

    if args.import_dir:
        # The snapshot is what makes the import reproduce the library's shape: the
        # payload is files only. Keep it beside the content directory — a files
        # source migrates every file it finds, so one *inside* would be content.
        snapshot_path = args.structure or structure_path(args.import_dir)
        structure = load_list_structure(snapshot_path) if os.path.isfile(snapshot_path) else None
        if structure is not None:
            print(f"Structure: {snapshot_path}")
        options = MigrationOptions(concurrency=args.concurrency)
        job = MigrationJob(
            FileSystemSource(args.import_dir),
            SharePointLibraryTarget(
                folder,
                concurrency=args.concurrency,
                sp_list=ctx.web.get_list(args.library_url).get().execute_query() if structure else None,
                structure=structure,
            ),
            options=options,
        )
        print(f"Importing {args.import_dir} -> {args.library_url}")
    else:
        # Export mirrors the library — overwrite a previous export rather than
        # skip on stale files.
        options = MigrationOptions(concurrency=1, conflict_resolution=ConflictResolution.OVERWRITE)
        job = MigrationJob(
            SharePointLibrarySource(folder),
            FileSystemTarget(args.target, include_folders=True),
            options=options,
        )
        print(f"Exporting {args.library_url} -> {args.target}")

    print("Planning…", flush=True)
    manifest = job.plan()
    print(f"Planned {len(manifest)} files/folders")

    print("Migrating…", flush=True)
    stats = job.run()
    print(stats.summary())
    print(job.verify().summary())

    if not args.import_dir:
        snapshot = save_list_structure(
            capture_list_structure(ctx.web.get_list(args.library_url)), structure_path(args.target)
        )
        print(f"Structure: {snapshot}")


if __name__ == "__main__":
    main()
