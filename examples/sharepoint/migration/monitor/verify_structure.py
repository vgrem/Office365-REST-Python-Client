"""
Verify that a target list reproduces the source list's structure (read-only).

Compares the **columns**, **content types**, **views** and **container settings**
(versioning, moderation, attachments, item-level read/write security, draft
visibility, list validation, library minor versions / required check-out) captured
from the source and target lists and reports what the target is missing — a
post-migration check that content-level verification (item counts / checksums)
cannot see. Nothing is written; only GET requests are issued.

    python verify_structure.py --list Projects --target-site https://contoso.sharepoint.com/sites/projects-copy
    python verify_structure.py --all --source-site https://contoso.sharepoint.com/sites/src --target-site https://contoso.sharepoint.com/sites/dst

Exits non-zero when any list is missing structure, so it can gate a migration
pipeline. Only *missing* structure is reported: a freshly created target list
legitimately carries extra built-in columns/content types/views.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

from __future__ import annotations

import argparse
import sys

from office365.migration.sharepoint import verify_list_structure
from office365.migration.sharepoint.resolvers import is_migratable_list
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def _connect(url: str) -> ClientContext:
    return ClientContext(url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )


def main():
    parser = argparse.ArgumentParser(description="Verify target list structure against the source")
    parser.add_argument("--list", dest="list_title", default="Documents", help="list/library title (default: Documents)")
    parser.add_argument("--all", action="store_true", help="verify every migratable list/library")
    parser.add_argument("--source-site", default=site_url, help="source site URL")
    parser.add_argument("--target-site", required=True, help="target site URL")
    args = parser.parse_args()

    source_ctx = _connect(args.source_site)
    target_ctx = _connect(args.target_site)

    if args.all:
        titles = [entry.title for entry in source_ctx.web.lists.get().execute_query() if is_migratable_list(entry)]
    else:
        titles = [args.list_title]

    failed = 0
    for title in titles:
        source_list = source_ctx.web.lists.get_by_title(title)
        target_list = target_ctx.web.lists.get_by_title(title)
        try:
            report = verify_list_structure(source_list, target_list)
        except Exception as e:  # noqa: BLE001 — a missing target list is a finding, not a crash
            print(f"{title}: could not verify ({e})")
            failed += 1
            continue

        status = "OK" if report.ok else "MISMATCH"
        print(f"[{status}] {title}: {report.summary()}")
        if not report.ok:
            for label, items in (
                ("missing column", report.missing_columns),
                ("differing column", report.column_mismatches),
                ("missing content type", report.missing_content_types),
                ("missing view", report.missing_views),
                ("missing field link", report.missing_field_links),
                ("differing setting", report.settings_mismatches),
            ):
                for item in items:
                    print(f"    {label}: {item}")
            failed += 1

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
