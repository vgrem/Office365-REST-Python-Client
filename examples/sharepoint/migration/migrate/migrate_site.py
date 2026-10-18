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
no target page is deleted. A publishing page (or a page with neither a canvas nor
a wiki body) cannot be copied — it needs page transformation — so it is reported
as a handoff, as are the client-side web parts whose data bindings point at the
source site (and the wiki markup that hard-codes it).

Each web's ``Title`` and ``Description`` are copied onto the target web when they
differ (``--no-site-settings`` to leave the target web's own values), and so is its
branding — master page, logo, alternate CSS and theme folder — rebased onto the
target's path and written only where the target actually resolves the asset it
names; one it does not is reported instead (``SiteLogoUrl`` is often the site's
group image, a service endpoint with no counterpart to copy). Site-collection and
regional settings stay outside a client-side content migration and are reported as
such.

Each web's site pages are copied too (``--no-pages`` to only report them). A
modern page is created through the ``sitepages`` endpoint and gets its canvas and
metadata; a classic wiki page is created with its ``WikiField`` body, copied
verbatim. Both are published when the source page was. A page whose name already
exists on the target is renamed around it (``--duplicate-pages`` to skip or
overwrite instead).

Resolution also reports what a copy cannot carry — publishing pages, web part data
bindings, workflow associations, InfoPath forms and business-data (BCS) external
lists — as one warning per category in the run's warning list.

While it runs, ``--stats`` prints a heartbeat per active list that names the list and
its position in the run (``[ 4/24] Documents  migrating  412/1,010 (40.8%)  9.7
it/s  ETA 1m02s``), and each list prints a closing line the moment it finishes
(``✓ [ 4/24] Documents  1,010 copied  1m42s  9.9 it/s  2.4 MB/s``) instead of a
status dump at the end; a repeated warning is printed once with a count.
``--log-json`` turns the same events into JSON lines on stderr — one object per
event, with the run/job/plan boundaries and every failure — for whatever collects
logs on the machine (an OpenTelemetry Collector, Promtail, ``kubectl logs``);
``--log-level DEBUG`` without it prints those events as plain lines instead, so a
watched run needs no collector to be verbose. The checkpoint and manifest files stay
the authoritative record; the log is for watching a run, not for resuming one.

``--concurrency N`` (default 1) and ``--batch-size N`` (default 100) tune the copy,
and each list's closing line reports the rate it actually achieved (``1m42s,
9.9 it/s, 2.4 MB/s``), so a change can be judged on a number instead of a hunch.
``--lists-in-flight N`` (default 1) is the site-level knob: a site of many small
lists spends its time on round trips — resolving each list's structure, then
copying a few hundred items — so migrating several lists at once is what shortens
the run. Each list keeps its own manifest and checkpoint, and every worker gets its
own context clone (same transport, same rate limiter), so parallelism does not
change what the target receives.

Two throttling knobs make that number honest: the run counts the responses the
service answered with ``429``/``503`` and the ``Retry-After`` seconds it asked for
(``ThrottleMonitor``), reporting them in the summary and as ``throttled`` events, so
a rate the service limited is not mistaken for the rate the target allows; and
``--pace SECONDS`` puts a floor between requests across all workers, which is the
proactive lever for a tenant that throttles a parallel run.
"""

from __future__ import annotations

import argparse
import logging
import time
from collections import Counter
from pathlib import Path

from office365.migration import MigrationOptions, MigrationSession, MigrationSettings, ThrottleMonitor
from office365.migration.logging import (
    ProgressReporter,
    configure_json_logging,
    configure_text_logging,
    log_event,
)
from office365.migration.sharepoint.pages import (
    PAGE_LIBRARY_TEMPLATE,
    capture_home_page,
    capture_site_pages,
)
from office365.migration.sharepoint.resolvers import is_document_library, is_migratable_list
from office365.migration.tasks import MigrationTask
from office365.runtime.http.throttling import RateLimiter
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, team_site_url, tenant


def _csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def _parser() -> argparse.ArgumentParser:
    """The command line: what to migrate, what to preserve and how to report it."""
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
        help="only report the source's site pages instead of copying them",
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
    parser.add_argument(
        "--lists-in-flight",
        type=int,
        default=1,
        metavar="N",
        help="lists migrated at the same time (default: 1; raise it to stop paying resolution and round trips serially)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        metavar="N",
        help="parallel workers per list (default: 1; raise it for many small files)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        metavar="N",
        help="items per $batch / progress/checkpoint flush (default: 100)",
    )
    parser.add_argument(
        "--pace",
        type=float,
        default=0.0,
        metavar="SECONDS",
        help="minimum interval between requests across all workers (default: 0, no pacing)",
    )
    parser.add_argument(
        "--stats",
        type=float,
        default=15.0,
        metavar="SECONDS",
        help="progress heartbeat interval per list (default: 15; 0 disables)",
    )
    parser.add_argument(
        "--log-json",
        nargs="?",
        const="-",
        metavar="PATH",
        help="write structured migration events as JSON lines (default: stderr)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="minimum level for the run's events; DEBUG without --log-json prints them as plain lines (default: INFO)",
    )
    parser.add_argument("--apply", action="store_true", help="perform the migration (default: dry run)")
    parser.add_argument("--no-verify", action="store_true", help="skip the post-run source/target reconciliation")
    return parser


def main():
    args = _parser().parse_args()

    include = _csv(args.include)
    exclude = _csv(args.exclude)
    preserve_timestamps = args.preserve or args.preserve_timestamps
    preserve_authorship = args.preserve or args.preserve_authorship
    preserve_permissions = args.preserve or args.preserve_permissions
    preserving = [
        name
        for name, on in (
            ("timestamps", preserve_timestamps),
            ("authorship", preserve_authorship),
            ("permissions", preserve_permissions),
        )
        if on
    ]

    level = getattr(logging, args.log_level)
    if args.log_json:
        stream = None
        if args.log_json != "-":
            stream = open(args.log_json, "a", encoding="utf-8")  # noqa: SIM115 — closed at process exit
        configure_json_logging(stream, level=level)
    elif args.log_level == "DEBUG":
        # --log-level is not a silent no-op: verbose events as plain lines on stderr.
        configure_text_logging(level=level)

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

    print_lines = _PlanPrinter(args, preserving)
    print_lines(source_ctx.web, all_lists, lists, subwebs)
    if not args.apply:
        print(f"\nDry run — nothing was written. Re-run with --apply to migrate {len(lists)} list(s).")
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
    options = MigrationOptions(concurrency=max(1, args.concurrency), batch_size=max(1, args.batch_size))
    # Clone-aware: every web the resolver resolves shares this transport.
    throttle = ThrottleMonitor().attach(ctx)
    if args.pace > 0:
        limiter = RateLimiter(min_interval=args.pace)
        limiter.bind(ctx)
    session = MigrationSession(options, throttle=throttle).register(context=ctx, settings=fidelity)
    # The reporter covers the plan as well as the copy: resolution provisions every
    # target container and replays its structure, which used to be the quiet phase.
    console = _Console(session)
    reporter = ProgressReporter(interval=args.stats, emit=console) if args.stats else None
    # Resolution provisions the target's containers and replays each list's
    # structure, so it is part of the run an operator is watching, not a prologue.
    print(f"\nMigrating into {args.target_site}…", flush=True)
    jobs = session.add_site_task(
        task=MigrationTask.sharepoint(args.source_site, args.target_site, migrate_all=True),
        include=include,
        exclude=exclude,
        provision_structure=not args.no_provision_structure,
        include_subwebs=args.include_subwebs,
        manifest_dir=work / "manifests",
        checkpoint_dir=work / "checkpoints",
        progress=reporter,
    )
    console.bind(jobs)

    started = time.monotonic()
    session.start(progress=reporter, concurrency=max(1, args.lists_in_flight))
    console.report_finished()
    _print_delta(session)
    _apply_list_security(source_ctx, ctx, preserve_permissions)

    if not args.no_verify:
        _report_verification(session, source_ctx, ctx, preserve_permissions, fidelity)

    _print_warnings(session.warnings(), structured=bool(args.log_json))
    _print_outcome(session.show(), throttle, time.monotonic() - started)


_TERMINAL_PHASES = {"COMPLETED", "COMPLETED_WITH_ERRORS", "CANCELLED", "FAILED"}
#: Longest name column: past this, one long library name would push every line out.
_LABEL_WIDTH = 28
_SECONDS_PER_HOUR = 3600
#: Below this a per-second byte rate renders as "0.0 MB/s", which says nothing.
_MIN_MB_PER_SECOND = 0.05


def _short_label(label) -> str:
    """``list:Documents`` or ``library:/sites/t/Documents`` -> ``Documents``."""
    text = str(label or "")
    kind, _, tail = text.partition(":")
    leaf = tail.rstrip("/").rsplit("/", 1)[-1] if tail else kind
    return leaf or text


def _label_width(labels) -> int:
    """The name column width for a set of labels (capped, never negative)."""
    return min(_LABEL_WIDTH, max((len(_short_label(label)) for label in labels), default=0))


def _fit(text: str, width: int) -> str:
    """Pad or elide ``text`` to ``width`` so a column stays a column."""
    if len(text) <= width:
        return text.ljust(width)
    return text[: max(0, width - 1)] + "…"


class _PlanPrinter:
    """Print what the run is about to do: the inventory, the pages and the knobs.

    A dry run and a real run share it, so the inventory an operator approves is the
    inventory the run reports against — same names, same order.
    """

    def __init__(self, args, preserving: list[str]) -> None:
        self._args = args
        self._preserving = preserving

    def __call__(self, source_web, all_lists, lists, subwebs) -> None:
        args = self._args
        print(f"source  {args.source_site}")
        print(f"target  {args.target_site}")
        print(f"\nLists ({len(lists)})")
        for entry in lists:
            kind = "library" if is_document_library(entry) else "list"
            print(f"  {kind:<7}  {entry.title}")
        if not lists:
            print("  (none)")
        if not args.no_pages:
            self._pages(source_web, all_lists)
        if subwebs:
            action = (
                "mirrored (with their nested subsites)"
                if args.include_subwebs
                else "skipped — pass --include-subwebs to mirror them"
            )
            names = ", ".join(web.title for web in subwebs)
            print(f"\nSubsites ({len(subwebs)}, {action})")
            print(f"  {names}")
        self._options()

    def _pages(self, source_web, all_lists) -> None:
        pages = [
            page
            for entry in all_lists
            if entry.base_template == PAGE_LIBRARY_TEMPLATE and not entry.hidden
            for page in capture_site_pages(entry)
        ]
        print(f"\nPages ({len(pages)})")
        if pages:
            classic = sum(1 for page in pages if page.is_classic)
            detail = f"{len(pages)} site page(s) copied"
            if classic:
                detail += f", {classic} classic wiki"
            print(f"  {detail} (duplicates: {self._args.duplicate_pages.lower()})")
        else:
            print("  (none)")
        home = capture_home_page(source_web)
        if home:
            print(f"  home  {home} follows the copy")

    def _options(self) -> None:
        args = self._args
        print("\nOptions")
        if self._preserving:
            print(f"  preserve  {', '.join(self._preserving)} (best-effort)")
        tuning = f"lists in flight {args.lists_in_flight}, concurrency {args.concurrency}, batch {args.batch_size}"
        if args.pace > 0:
            tuning += f", pace {args.pace:g}s"
        print(f"  copy      {tuning}")


class _Console:
    """The console view of a run: a heartbeat per list, a line as each one finishes.

    A heartbeat names the list it belongs to and where that list sits in the run, so
    a line answers "what is being copied" and not only "how far along is something".
    Completion is read from the session's statuses, which is what lets a finished
    list print its own line at the moment it finished, instead of a status dump at
    the end of the run.
    """

    def __init__(self, session) -> None:
        self._session = session
        self._total = 0
        self._width = _LABEL_WIDTH
        self._position: dict[str, int] = {}
        self._finished: set[str] = set()

    def bind(self, jobs) -> None:
        """Attach the run's jobs (known only once the site task is resolved)."""
        labels = [job.target_label for job in jobs]
        self._total = len(labels)
        self._position = {_short_label(label): index for index, label in enumerate(labels, start=1)}
        self._width = _label_width(labels)

    def __call__(self, beat: dict) -> None:
        subject = _short_label(beat.get("label") or beat.get("subject"))
        total = beat.get("total")
        if not total or beat["done"] < total:
            self._line(self._head(subject), self._beat(beat))
        self.report_finished()

    def report_finished(self) -> None:
        """Print every list that reached a terminal phase, once."""
        for status in self._session.show():
            label = status["target"]
            if status["phase"] in _TERMINAL_PHASES and label not in self._finished:
                self._finished.add(label)
                mark = "!" if status["stats"]["errors"] else "✓"
                self._line(f"{mark} {self._head(_short_label(label))}", self._result(status))

    def _line(self, head: str, body: str) -> None:
        print(f"  {head}  {body}".rstrip(), flush=True)

    def _head(self, subject: str) -> str:
        position = self._position.get(subject)
        if position is None:
            # A resolution step reports before the run's jobs exist: name the list,
            # but do not imply a position it does not have.
            return _fit(subject, self._width)
        return f"[{position:>3}/{self._total}] {_fit(subject, self._width)}"

    def _beat(self, beat: dict) -> str:
        done = f"{beat['done']:,}"
        if beat.get("total"):
            done += f"/{beat['total']:,} ({beat['percent']}%)"
        parts = [beat.get("stage") or "copying", done]
        if beat.get("rate"):
            parts.append(f"{beat['rate']:g} it/s")
        eta = beat.get("eta_seconds")
        if eta is not None:
            parts.append("ETA <1s" if eta < 1 else f"ETA {_eta(eta)}")
        return "   ".join(parts)

    def _result(self, status: dict) -> str:
        stats = status["stats"]
        parts = [f"{stats['success']:,} copied"]
        if stats["skipped"]:
            parts.append(f"{stats['skipped']:,} skipped")
        if stats["errors"]:
            parts.append(f"{stats['errors']:,} failed")
        parts.extend(_throughput(status))
        return "   ".join(parts)


def _throughput(status: dict) -> list[str]:
    """``1m42s``, ``1.7 it/s``, ``0.4 MB/s`` — how fast this list actually went."""
    duration_ms = status.get("duration_ms")
    if not duration_ms:
        return []
    seconds = max(duration_ms / 1000, 0.001)
    stats = status["stats"]
    parts = [_elapsed(seconds)]
    handled = stats["success"] + stats["skipped"]
    if handled:
        parts.append(f"{handled / seconds:.1f} it/s")
    megabytes = stats["bytes_transferred"] / seconds / 1024 / 1024
    if megabytes >= _MIN_MB_PER_SECOND:
        parts.append(f"{megabytes:.1f} MB/s")
    return parts


def _elapsed(seconds: float) -> str:
    """``102`` -> ``"1m42s"`` — a duration readable at a glance."""
    seconds = int(round(seconds))
    minutes, rest = divmod(seconds, 60)
    return f"{minutes}m{rest:02d}s" if minutes else f"{rest}s"


def _eta(seconds: float) -> str:
    """An ETA in the unit that fits: seconds, minutes, or hours."""
    if seconds >= _SECONDS_PER_HOUR:
        return f"{seconds / _SECONDS_PER_HOUR:.1f}h"
    return _elapsed(seconds)


def _print_warnings(warnings: list[str], *, structured: bool = False) -> None:
    """Print the run's warnings, once each, with a count where one repeated.

    Structure replay reports the same rejection once per list that hits it; twelve
    copies of a line is not more information than one line and a number. With
    ``--log-json`` the same notes are also emitted as ``run.warning`` events, so a
    collector sees them without scraping the console.
    """
    if not warnings:
        return
    print(f"\nWarnings ({len(warnings)})", flush=True)
    for message, count in Counter(warnings).items():
        print(f"  ×{count}  {message}" if count > 1 else f"     {message}")
        if structured:
            log_event("run.warning", message, level=logging.WARNING, count=count)


def _print_outcome(statuses, monitor: ThrottleMonitor, seconds: float) -> None:
    """The closing block: what was copied, and what the service said about the pace."""
    totals = {"success": 0, "skipped": 0, "errors": 0}
    for status in statuses:
        for key in totals:
            totals[key] += status.get("stats", {}).get(key) or 0
    parts = [f"{totals['success']:,} copied"]
    if totals["skipped"]:
        parts.append(f"{totals['skipped']:,} skipped")
    if totals["errors"]:
        parts.append(f"{totals['errors']:,} failed")
    print(f"\nDone in {_elapsed(seconds)} — {', '.join(parts)} across {len(statuses)} list(s)", flush=True)
    print(f"  {_throttling(monitor)}")


def _throttling(monitor: ThrottleMonitor) -> str:
    """``throttling: none (171 requests)`` or the monitor's counted summary."""
    if not monitor.throttled:
        return f"throttling: none ({monitor.responses:,} request(s))"
    return f"throttling: {monitor.summary()}"


def _apply_list_security(source_ctx, ctx, preserve_permissions: bool) -> None:
    """Replay each list's own ACLs — after the content, which is the only safe order.

    A list whose source permissions are unique (inheritance broken to restrict it)
    is the one ACL scope neither the web pass nor the item pass can reach: without
    this, a restricted library arrives readable at the web's permissions.
    """
    if not preserve_permissions:
        return
    from office365.migration.sharepoint.security import apply_site_list_security

    warnings: list[str] = []
    report = apply_site_list_security(source_ctx.web, ctx.web, warnings=warnings)
    print(f"\nPermissions: {report.summary()}", flush=True)
    for warning in warnings:
        print(f"     {warning}")


def _report_verification(session, source_ctx, ctx, preserve_permissions: bool, settings) -> None:
    """Reconcile every migrated list, plus the web-level concerns, with the source."""
    print("\nVerifying…", flush=True)
    statuses = session.show()
    width = _label_width(status["target"] for status in statuses)
    for status, report in zip(statuses, session.verify()):
        print(f"  {_fit(_short_label(status['target']), width)}  {report.summary()}")
        for path in report.missing[:5]:
            print(f"      missing: {path}")
        for path in report.extra[:5]:
            print(f"      extra:   {path}")
        for note in report.mismatches[:5]:
            print(f"      mismatch: {note}")
        for note in report.unverifiable[:3]:
            print(f"      unverified: {note}")
    _verify_web(source_ctx, ctx, preserve_permissions=preserve_permissions, settings=settings)


def _print_delta(session) -> None:
    """Print the drift a re-run found against the plan the previous run persisted."""
    for report in session.delta():
        for note in report.notes():
            print(f"  delta: {note}")


def _verify_web(source_ctx, ctx, *, preserve_permissions: bool, settings) -> None:
    """Reconcile every web-level concern the run claimed, in one report."""
    from office365.migration.sharepoint.site_verify import verify_site

    report = verify_site(
        source_ctx,
        ctx,
        settings=settings.migrate_site_settings != "NONE",
        branding=settings.migrate_site_settings != "NONE",
        navigation=settings.migrate_navigation,
        pages=settings.migrate_pages,
        security=preserve_permissions,
    )
    print(f"      site:     {report.summary()}")
    for note in report.issues:
        print(f"      {note}")
    for note in report.unverifiable:
        print(f"      unverified: {note}")


if __name__ == "__main__":
    main()
