"""
Export Teams to a resumable archive via the unified MigrationJob.

    python migrate/export_team.py --team <id> --output ./backup --files
    python migrate/export_team.py --all --output ./backup

Archive layout: ``<team-id>/team.json``, ``messages.ndjson``, ``attachments/``
and ``files/<channel>.zip`` (with ``--files``). Re-running resumes from the
checkpoint. Channel-level members are skipped by default — pass
``--channel-members`` (needs ``ChannelMember.Read.All``) to include them.

Requires application permissions: Team.ReadBasic.All, TeamMember.Read.All,
ChannelMessage.Read.All, Chat.Read.All (and Files.Read.All with --files).
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.teams import TeamsArchiveSource, TeamsArchiveTarget, TeamsExportOptions
from tests.settings import client_id, client_secret, tenant


def _build_job(client: GraphClient, args: argparse.Namespace) -> MigrationJob:
    options = TeamsExportOptions(
        include_files=args.files,
        include_messages=not args.no_messages,
        include_channel_members=args.channel_members,
    )
    source = TeamsArchiveSource(client, team_ids=args.team or None, options=options)
    target = TeamsArchiveTarget(args.output)
    out = Path(args.output)
    # Both the manifest (what to copy) and the checkpoint (what is done) are
    # persisted so --resume can pick up where the previous run stopped.
    return MigrationJob(
        source,
        target,
        manifest_path=out.with_name(out.name + ".manifest.json"),
        checkpoint_path=out.with_name(out.name + ".checkpoint.json"),
    )


def _execute(job: MigrationJob, resume: bool, *, with_files: bool) -> None:
    if resume:
        stats = job.resume()
    else:
        job.plan()
        stats = job.run()
    print(stats.summary())
    print(job.verify().summary())
    if with_files and stats.errors:
        print(
            "Note: channel file downloads need a SharePoint-backed channel drive "
            "(Files.Read.All); some tenants report 'no addressUrl for Microsoft.FileServices'."
        )


def main():
    parser = argparse.ArgumentParser(description="Export Teams to a resumable archive")
    parser.add_argument("--team", action="append", default=[], help="team id (repeatable)")
    parser.add_argument("--all", action="store_true", help="export every team in the tenant")
    parser.add_argument("--output", default=str(Path(tempfile.gettempdir()) / "teams_archive"), help="output directory")
    parser.add_argument("--files", action="store_true", help="also download channel files")
    parser.add_argument("--no-messages", action="store_true", help="skip messages")
    parser.add_argument(
        "--channel-members",
        action="store_true",
        help="include channel members (needs ChannelMember.Read.All)",
    )
    parser.add_argument("--resume", action="store_true", help="continue from the checkpoint")
    args = parser.parse_args()

    if not args.team and not args.all:
        parser.error("pass --team <id> (repeatable) or --all")

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    _execute(_build_job(client, args), args.resume, with_files=args.files)
    print(f"Archive: {args.output}")


if __name__ == "__main__":
    main()
