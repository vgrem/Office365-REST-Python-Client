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

A re-run against the same ``--work`` folder diffs its fresh plan against the one
the previous run persisted, so source-side deletions, renames/moves and edits are
named as ``delta`` notes instead of leaving stale target copies unnoticed.

Subsites are skipped unless ``--include-subwebs`` is given; the dry run names any
subsites it would leave behind.

Only the list *containers* are created on the target — fields, content types and
views are recreated from the source before content is copied
(``--no-provision-structure`` to only create the containers).

By default items get fresh target timestamps, authorship and inherited
descriptions. ``--preserve`` (or the individual ``--preserve-timestamps`` /
``--preserve-authorship`` / ``--preserve-permissions``) restores them from the
source on a best-effort basis; ``--preserve-permissions`` only copies items whose
source ACL is unique (inherited ACLs are left inheriting), and additionally
re-creates the site's custom groups, their membership and the web-level role
assignments. A post-run verification flags anything a requested facet could not
restore.

The source site's navigation (Quick Launch and top bar) is copied onto the target
(additively, source links rewritten to the target) unless the settings disable it;
a post-run reconciliation reports any link that did not land.

Modern site pages are copied too (canvas, title, description, layout, banner and
promoted state, published when the source page was), unless ``--no-pages`` is
given; a page whose name already exists follows ``--duplicate-pages``
(``RENAME`` — the default — ``SKIP`` or ``OVERWRITE``), and copies are add-only:
no target page is deleted. Classic pages (wiki/publishing pages) cannot be copied
— they need page transformation — so they are reported as a handoff, as are the
client-side web parts whose data bindings point at the source.

Each web's ``Title`` and ``Description`` are copied onto the target web when they
differ (``--no-site-settings`` to leave the target web's own values). Branding
(master page, theme, logo, alternate CSS) and the site-collection/regional
settings are outside a client-side content migration and are reported as such.

Each web's modern site pages are copied too (``--no-pages`` to only report them):
the page is created through the ``sitepages`` endpoint, its canvas and page
metadata are written, and it is published when the source page was. A page whose
name already exists on the target is renamed around it (``--duplicate-pages`` to
skip or overwrite instead).

Resolution also reports what a copy cannot carry — classic pages, web part data
bindings, workflow associations, InfoPath forms and business-data (BCS) external
lists — as one warning per category in the run's warning list.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from office365.migration import MigrationSession, MigrationSettings
from office365.migration.sharepoint.pages import PAGE_LIBRARY_TEMPLATE, capture_site_pages
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
    parser.add_argument(
        "--preserve",
        action="store_true",
        help="best-effort restore of item timestamps, authorship and unique permissions",
    )
    parser.add_argument(
        "--preserve-timestamps",
        action="store_true",
        help="restore each item's Created/Modified (client-side, best-effort)",
    )
    parser.add_argument(
        "--preserve-authorship",
        action="store_true",
        help="restore each item's Author/Editor (client-side, best-effort)",
    )
    parser.add_argument(
        "--preserve-permissions",
        action="store_true",
        help="copy item *unique* role assignments and re-create the site's groups/role assignments",
    )
    parser.add_argument(
        "--no-pages",
        action="store_true",
        help="only report the source's modern site pages instead of copying them",
    )
    parser.add_argument(
        "--no-site-settings",
        action="store_true",
        help="leave the target web's own Title/Description instead of copying the source's",
    )
    parser.add_argument(
        "--duplicate-pages",
        choices=["RENAME", "SKIP", "OVERWRITE"],
        default="RENAME",
        help="what to do when a target page of that name exists (default: RENAME)",
    )
    parser.add_argument("--apply", action="store_true", help="perform the migration (default: dry run)")
    parser.add_argument("--no-verify", action="store_true", help="skip the post-run source/target reconciliation")
    args = parser.parse_args()

    include = _csv(args.include)
    exclude = _csv(args.exclude)
    preserve_timestamps = args.preserve or args.preserve_timestamps
    preserve_authorship = args.preserve or args.preserve_authorship
    preserve_permissions = args.preserve or args.preserve_permissions

    ctx = ClientContext(args.target_site).with_client_certificate(tenant, client_id, cert_thumbprint, cert_path)

    # Plan: read the source site's lists directly (no target writes on a dry run).
    source_ctx = ctx.clone(args.source_site)
    all_lists = source_ctx.web.lists.get().execute_query()
    lists = [entry for entry in all_lists if is_migratable_list(entry)]
    if include:
        lists = [entry for entry in lists if entry.title in include]
    if exclude:
        lists = [entry for entry in lists if entry.title not in exclude]
    subwebs = list(source_ctx.web.webs.get().execute_query())

    print(f"{args.source_site} -> {args.target_site}")
    for entry in lists:
        print(f"  {'library' if is_document_library(entry) else 'list':7} {entry.title}")
    _print_pages(all_lists, copy=not args.no_pages, duplicate=args.duplicate_pages)
    if subwebs:
        action = (
            "will be mirrored (including their nested subsites)"
            if args.include_subwebs
            else "will be skipped (pass --include-subwebs)"
        )
        print(f"  {len(subwebs)} direct subsite(s) {action}: {', '.join(web.title for web in subwebs)}")
    if not lists and not (subwebs and args.include_subwebs):
        print("  (nothing to migrate)")
    preserving = [
        name
        for name, on in (
            ("timestamps", preserve_timestamps),
            ("authorship", preserve_authorship),
            ("permissions", preserve_permissions),
        )
        if on
    ]
    if preserving:
        print(f"  preserving (best-effort): {', '.join(preserving)}")
    if not args.apply:
        print(f"\nDry run — {len(lists)} list(s). Re-run with --apply to migrate (--include/--exclude to narrow).")
        return

    work = Path(args.work)
    fidelity = MigrationSettings(
        preserve_timestamps=preserve_timestamps,
        preserve_authorship=preserve_authorship,
        preserve_permissions=preserve_permissions,
        migrate_pages=not args.no_pages,
        migrate_site_settings="NONE" if args.no_site_settings else "PRESERVE_ALL_SETTINGS",
        duplicate_page_behavior=args.duplicate_pages,
    )
    session = MigrationSession().register(context=ctx, settings=fidelity)
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
    _print_delta(session)

    if not args.no_verify:
        _report_verification(session, source_ctx, ctx, preserve_permissions, fidelity)

    for warning in session.warnings():
        print(f"  warning: {warning}")


def _report_verification(session, source_ctx, ctx, preserve_permissions: bool, settings) -> None:
    """Reconcile every migrated list, plus the web-level concerns, with the source."""
    print("\nVerifying…", flush=True)
    for status, report in zip(session.show(), session.verify()):
        print(f"  {status['target']}: {report.summary()}")
        for path in report.missing[:5]:
            print(f"      missing: {path}")
        for path in report.extra[:5]:
            print(f"      extra:   {path}")
        for note in report.mismatches[:5]:
            print(f"      mismatch: {note}")
        for note in report.unverifiable[:3]:
            print(f"      unverified: {note}")
    _verify_web_scope(source_ctx, ctx, preserve_permissions, settings.migrate_navigation)
    if settings.migrate_site_settings != "NONE":
        _verify_site_settings(source_ctx, ctx)
    if settings.migrate_pages:
        _verify_pages(source_ctx, ctx)


def _print_pages(all_lists, *, copy: bool, duplicate: str) -> None:
    """Print how many modern site pages the run would copy (dry run reads only)."""
    if not copy:
        return
    pages = [
        page
        for entry in all_lists
        if entry.base_template == PAGE_LIBRARY_TEMPLATE and not entry.hidden
        for page in capture_site_pages(entry)
    ]
    if pages:
        print(f"  pages:   {len(pages)} modern site page(s) will be copied (duplicates: {duplicate})")


def _print_delta(session) -> None:
    """Print the drift a re-run found against the plan the previous run persisted."""
    for report in session.delta():
        for note in report.notes():
            print(f"  delta: {note}")


def _verify_web_scope(source_ctx, ctx, preserve_permissions: bool, migrate_navigation: bool) -> None:
    """Reconcile the resolver-level web concerns (site security, navigation) with the source."""
    if preserve_permissions:
        _verify_site_security(source_ctx, ctx)
    if migrate_navigation:
        _verify_navigation(source_ctx, ctx)


def _verify_site_security(source_ctx, ctx) -> None:
    """Reconcile the migrated web's groups/role assignments against the source."""
    from office365.migration.sharepoint.security import verify_site_security

    for note in verify_site_security(source_ctx.web, ctx.web):
        print(f"  site: {note}")


def _verify_site_settings(source_ctx, ctx) -> None:
    """Reconcile the target web's Title/Description against the source."""
    from office365.migration.sharepoint.site_settings import verify_web_settings

    for note in verify_web_settings(source_ctx.web, ctx.web):
        print(f"  {note}")


def _verify_pages(source_ctx, ctx) -> None:
    """Reconcile the migrated web's modern site pages against the source."""
    from office365.migration.sharepoint.pages import verify_page_copy

    for note in verify_page_copy(source_ctx.web, ctx.web):
        print(f"  pages: {note}")


def _verify_navigation(source_ctx, ctx) -> None:
    """Reconcile the migrated web's navigation against the source."""
    from office365.migration.sharepoint.navigation import verify_navigation

    for note in verify_navigation(source_ctx.web, ctx.web):
        print(f"  nav: {note}")


if __name__ == "__main__":
    main()
