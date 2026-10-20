"""
Import a portable ICS tree into a calendar, recreating events and their series.

The tree is the one `examples/outlook/migration/export` writes: ``.ics`` files plus
their JSON sidecars. The sidecar is the contract — it carries Graph's recurrence
object, which iCalendar cannot express — so an ``.ics`` on its own is refused. The
import is the same ``MigrationJob``, so it plans, resumes and verifies: a re-run
skips what the calendar already has, and ``verify()`` compares a digest of the
restorable fields rather than the ``.ics`` bytes (Exchange re-serializes the body).

What survives the round trip: the time range and its zone, subject, body, location,
show-as, sensitivity, importance, the reminder, Outlook categories and the
recurrence of a series. What does not: the attendees (restoring them makes Exchange
send a real invitation to every one of them — measured — so it is opt-in), and the
meeting metadata Exchange assigns itself (``iCalUId``, organizer, responses, the
created/modified times).

Requires delegated permission ``Calendars.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/user-post-events
"""

import argparse
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import CalendarImportOptions, CalendarTarget, IcsTreeSource
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Import an ICS tree into a calendar")
    parser.add_argument("--source", required=True, help="directory of exported .ics files")
    parser.add_argument("--calendar", default=None, help="calendar id (default: the user's default calendar)")
    parser.add_argument("--attendees", action="store_true", help="also invite the attendees (sends invitations)")
    parser.add_argument("--no-categories", action="store_true", help="do not restore Outlook categories")
    parser.add_argument("--no-transaction-ids", action="store_true", help="do not send a deduplicating transactionId")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    calendar = (
        client.me.calendars[args.calendar].get().execute_query()
        if args.calendar
        else client.me.calendar.get().execute_query()
    )
    source = Path(args.source)

    # One options object, shared by both adapters: the verification digest counts
    # attendees and categories only when the options say the import restores them.
    options = CalendarImportOptions(
        restore_attendees=args.attendees,
        restore_categories=not args.no_categories,
        use_transaction_ids=not args.no_transaction_ids,
    )
    job = MigrationJob(IcsTreeSource(source, options), CalendarTarget(calendar, options))

    job.plan()
    print(f"Planned {len(job.manifest)} events from {source}")
    stats = job.run()
    print(stats.summary())

    report = job.verify()
    print(report.summary())
    print(f"Imported into {calendar.name}")


if __name__ == "__main__":
    main()
