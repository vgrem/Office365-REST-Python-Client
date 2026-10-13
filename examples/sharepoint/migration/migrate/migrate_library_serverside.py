"""
Migrate a local folder into a SharePoint document library — server-side.

The whole SharePoint Migration API flow in five steps:
  1. authenticate (app-only)      2. resolve the target web + library
  3. provision SharePoint-owned containers (no Azure account needed)
  4. package + submit: files -> manifest XML -> blobs -> ingestion job
  5. monitor until the job finishes

Defaults to the repo sample data (``examples/data``) and the ``Documents``
library — run it from this folder. It needs a real tenant; for a tenant-free look
at the package it builds, see the offline ``package_library.py`` example.

Requires: a ``.env`` with ``OFFICE365_TENANT`` / ``OFFICE365_CLIENT_ID`` /
``OFFICE365_CERT_THUMBPRINT`` and ``tests/selfsigncert.pem``; the app
registration needs the application permission **Sites.FullControl.All**.

    python migrate_library_serverside.py
    python migrate_library_serverside.py --source ./my-files --library "Shared Documents"

https://learn.microsoft.com/en-us/sharepoint/dev/apis/migration-api-overview
"""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from office365.migration import MigrationJob
from office365.migration.adapters.filesystem import FileSystemSource
from office365.migration.sharepoint.package_target import SharePointPackageTarget
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def _progress(progress) -> None:
    print(f"  {progress.stage}: {progress.done}/{progress.total or '?'}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Server-side migration into a document library")
    parser.add_argument("--source", default="../../../data", help="local folder (default: examples/data)")
    parser.add_argument("--library", default="Documents", help="library title")
    args = parser.parse_args()

    source = Path(args.source)
    if not source.is_dir():
        parser.error(f"not a directory: {source} — run this script from its own folder, or pass --source")

    # 1. Authenticate — the Migration API needs app-only auth.
    ctx = ClientContext(site_url).with_client_certificate(tenant, client_id, cert_thumbprint, cert_path)

    # 2. Resolve the target web + library (and the library root folder's ids).
    web = ctx.web.get().execute_query()
    library = ctx.web.get_list_by_title(args.library).get().execute_query()
    root = library.root_folder
    root.ensure_properties(["UniqueId", "ServerRelativeUrl"]).execute_query()
    parent = root.parent_folder.ensure_property("UniqueId")
    parent.execute_query()
    library_url = root.server_relative_url
    print(f"Target: {library.title}  ({library_url}, web {web.id})")

    # 3. Provision SharePoint-owned Azure containers (SAS URIs + encryption key).
    containers = ctx.site.provision_migration_containers().execute_query().value

    # 4. Package + submit: local files -> manifest XML -> staged blobs -> ingestion job.
    target = SharePointPackageTarget(
        ctx.site,
        web.id,
        content_uri=containers.DataContainerUri,
        manifest_uri=containers.MetadataContainerUri,
        encryption_key=containers.EncryptionKey,
        site_url=site_url,
        list_title=library.title or args.library,
        list_url=library_url,
        web_url=urlparse(site_url).path or "/",
        root_folder_id=root.unique_id,
        root_folder_parent_id=parent.unique_id,
        source_type="FileShare",
    )
    job = MigrationJob(FileSystemSource(str(source)), target)
    print(f"Planning {source}… {len(job.plan())} files")
    print("Packaging + submitting…")
    job.run()
    print(f"  ingestion job {target.job_id}")

    # 5. Monitor until the job is terminal; explain a failure.
    print("Monitoring…")
    status = target.monitor(interval=30, progress=_progress)
    print(f"  {status}")
    if status == "failed":
        print("\n".join(f"  {line}" for line in target.diagnose()))


if __name__ == "__main__":
    main()
