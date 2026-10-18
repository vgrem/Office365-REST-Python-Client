"""
Export a calendar as a portable ICS tree.

Each event lands as ``<calendar>/<date>_<subject>_<id>.ics`` plus a JSON sidecar
carrying what iCalendar cannot (Graph ids, the recurrence object, the
online-meeting provider, sensitivity/importance), and the run ends with a
``manifest.jsonl`` index. ``.ics`` opens in Outlook, Google Calendar and
Thunderbird, so the export is both an archive and the input for an import.

The job is the same ``MigrationJob`` the SharePoint and mail adapters use, so it
plans, resumes and verifies: a re-run skips what is already on disk, and
``verify()`` compares each ``.ics`` checksum against the document rendered from
the source event.

Requires delegated permission ``Calendars.Read``.

https://learn.microsoft.com/en-us/graph/api/user-list-events
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob, MigrationOptions
from office365.migration.outlook import CalendarExportOptions, CalendarSource, IcsExportTarget
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Export a calendar to an ICS tree")
    parser.add_argument("--calendar", default=None, help="calendar id (default: the user's default calendar)")
    parser.add_argument("--output", default=None, help="output directory (default: temp dir)")
    parser.add_argument("--root-name", default=None, help="top folder name (default: the calendar's display name)")
    parser.add_argument("--instances", action="store_true", help="also export recurring occurrences/exceptions")
    parser.add_argument("--cancelled", action="store_true", help="also export cancelled events")
    parser.add_argument("--preserve-timestamps", action="store_true", help="stamp each .ics with its modified time")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    calendar = (
        client.me.calendars[args.calendar].get().execute_query()
        if args.calendar
        else client.me.calendar.get().execute_query()
    )
    output = Path(args.output or tempfile.mkdtemp(prefix="calendar-export-"))

    options = CalendarExportOptions(
        root_name=args.root_name,
        include_recurring_instances=args.instances,
        include_cancelled=args.cancelled,
    )
    job = MigrationJob(
        CalendarSource(calendar, options),
        IcsExportTarget(output),
        options=MigrationOptions(preserve_timestamps=args.preserve_timestamps),
    )

    job.plan()
    print(f"Planned {len(job.manifest)} events from {calendar.name}")
    stats = job.run()
    print(stats.summary())
    print(job.verify().summary())
    print(f"Export written to {output}")


if __name__ == "__main__":
    main()
