"""
Whole-site migration (same tenant) — every list and document library from one
site collection to another, one resumable job per list.

This is the ``migrate_all`` task shape: register a target session, add a
SharePoint task covering the whole source site, then start it. Each list gets
its own manifest and checkpoint, so a large site resumes per list.

    python migrate_site.py --source-site https://contoso.sharepoint.com/sites/source
    python migrate_site.py --source-site ... --apply

Dry-run by default: it lists the lists/libraries that would migrate and creates
nothing. ``--apply`` performs the copy, persisting per-list state under
``--work`` so an interrupted run resumes. After a run it reconciles every list
against the source (presence via the ``MigrationSourceId`` marker, plus attachment
checksums) and prints any adapter warnings; pass ``--no-verify`` to skip it.

Subsites are skipped unless ``--include-subwebs`` is given; the dry run names any
subsites it would leave behind.

Only the list *containers* are created on the target — fields, content types and
views are recreated from the source before content is copied
(``--no-provision-structure`` to only create the containers).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from office365.migration import MigrationSession, MigrationSettings
from office365.migration.sharepoint.resolvers import is_document_library, is_migratable_list
from office365.migration.tasks import MigrationTask
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, team_site_url, tenant


def _csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def main():
    parser = argparse.ArgumentParser(description="Whole-site (same-tenant) SharePoint migration")
    parser.add_argument("--source-site", default=team_site_url, help="source site collection URL")
    parser.add_argument("--target-site", default=site_url, help="target site collection URL")
    parser.add_argument("--include", help="comma-separated list titles to migrate (default: all)")
    parser.add_argument("--exclude", help="comma-separated list titles to skip")
    parser.add_argument("--work", default=".migration", help="folder for manifests/checkpoints (default: .migration)")
    parser.add_argument(
        "--no-provision-structure",
        action="store_true",
        help="only create target list containers (skip columns/content types/views)",
    )
    parser.add_argument(
        "--include-subwebs",
        action="store_true",
        help="also mirror the source's subsites and migrate their lists",
    )
    parser.add_argument("--apply", action="store_true", help="perform the migration (default: dry run)")
    parser.add_argument("--no-verify", action="store_true", help="skip the post-run source/target reconciliation")
    args = parser.parse_args()

    include = _csv(args.include)
    exclude = _csv(args.exclude)

    ctx = ClientContext(args.target_site).with_client_certificate(tenant, client_id, cert_thumbprint, cert_path)

    # Plan: read the source site's lists directly (no target writes on a dry run).
    source_ctx = ctx.clone(args.source_site)
    lists = [entry for entry in source_ctx.web.lists.get().execute_query() if is_migratable_list(entry)]
    if include:
        lists = [entry for entry in lists if entry.title in include]
    if exclude:
        lists = [entry for entry in lists if entry.title not in exclude]

    print(f"{args.source_site} -> {args.target_site}")
    for entry in lists:
        print(f"  {'library' if is_document_library(entry) else 'list':7} {entry.title}")
    subwebs = list(source_ctx.web.webs.get().execute_query())
    if subwebs:
        action = "will be mirrored" if args.include_subwebs else "will be skipped (pass --include-subwebs)"
        print(f"  {len(subwebs)} subsite(s) {action}: {', '.join(web.title for web in subwebs)}")
    if not lists:
        print("  (nothing to migrate)")
    if not args.apply:
        print(f"\nDry run — {len(lists)} list(s). Re-run with --apply to migrate (--include/--exclude to narrow).")
        return

    work = Path(args.work)
    session = MigrationSession().register(context=ctx, settings=MigrationSettings())
    session.add_site_task(
        task=MigrationTask.sharepoint(args.source_site, args.target_site, migrate_all=True),
        include=include,
        exclude=exclude,
        provision_structure=not args.no_provision_structure,
        include_subwebs=args.include_subwebs,
        manifest_dir=work / "manifests",
        checkpoint_dir=work / "checkpoints",
    )

    print("\nMigrating…", flush=True)
    for status in session.start():
        stats = status["stats"]
        print(
            f"  [{status['phase']}] {status['source']} -> {status['target']} "
            f"success={stats['success']} skipped={stats['skipped']} errors={stats['errors']}"
        )

    if not args.no_verify:
        statuses = session.show()
        print("\nVerifying…", flush=True)
        for status, report in zip(statuses, session.verify()):
            print(f"  {status['target']}: {report.summary()}")
            for path in report.missing[:5]:
                print(f"      missing: {path}")
            for path in report.extra[:5]:
                print(f"      extra:   {path}")
            for note in report.mismatches[:5]:
                print(f"      mismatch: {note}")
            for note in report.unverifiable[:3]:
                print(f"      unverified: {note}")

    for warning in session.warnings():
        print(f"  warning: {warning}")


if __name__ == "__main__":
    main()
