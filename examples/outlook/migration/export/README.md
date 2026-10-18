# Export a mailbox or a calendar

Take a mailbox — or one folder and its subtree — out as a portable EML tree, or a
calendar out as an ICS tree; both open in any mail/calendar client and import
anywhere. Part of the [Outlook tour](../../README.md).

| What | File | Notes |
|------|------|-------|
| Folder → EML tree | [`export_folder_eml.py`](./export_folder_eml.py) | `--flat`, `--no-drafts`, `--preserve-timestamps`; ends with `manifest.jsonl` |
| Calendar → ICS tree | [`export_calendar_ics.py`](./export_calendar_ics.py) | `--root-name`, `--instances`, `--cancelled`; same index |

## What lands on disk

```text
<output>/
  Inbox/2024-03-01_Quarterly-report-Q1_cb65ad88.eml   # RFC 822 bytes
  Inbox/2024-03-01_Quarterly-report-Q1_cb65ad88.json  # the sidecar record
  Inbox/Archive/2023-12-24_Old-thread_1f9c07aa.eml
  manifest.jsonl                                       # one sidecar per line
```

The ``.eml`` is the message; the sidecar keeps what MIME does not carry — Graph
ids, read state, Outlook categories, conversation id, folder path — and
``manifest.jsonl`` is the index a later import reads.

```py
from office365.migration import MigrationJob
from office365.migration.outlook import MailExportTarget, MailFolderSource

job = MigrationJob(MailFolderSource(folder), MailExportTarget("./mailbox-export"))
job.plan()
job.run()
print(job.verify().summary())
```

Three things the job gives you for free, and why mail exports need them:

- **Resumable** — the plan is persisted and a re-run skips what is already on
  disk, so a throttled or interrupted export continues instead of restarting.
- **Verified** — `verify()` compares each exported file's MD5 against the source
  message's MIME, so "the export finished" is a measured claim, not a count.
- **Deterministic names** — `date_subject_iddigest.eml` is derived from the
  message, not from the enumeration order, so two runs land on the same paths.

## What the export deliberately does not do

- **Attachments are inside the MIME**, not separate files: they are part of the
  message, and splitting them would break the ``.eml`` contract.
- **No PST, no journaling/compliance capture.** Those are eDiscovery/Exchange
  admin surfaces; a REST client cannot produce ``.pst`` and should not pretend
  it can. If the target is Exchange, the Exchange **migration service** ingests
  the EML and is the right tool for the mailbox-wide move.
- **Categories are exported, not mapped.** A Gmail label with several parents has
  no Outlook equivalent (categories are a flat, many-to-many set); writing an
  M365-native category is a policy decision, so it belongs to the import step.
- **Drafts may not have an `internetMessageId`** — they are keyed by Graph id,
  which changes when the draft moves, so a re-run of a moved draft reports a
  second copy rather than overwriting the first.

## Calendar → ICS tree

```bash
uv run python examples/outlook/migration/export/export_calendar_ics.py --output ./calendar-export
```

```text
<output>/
  Calendar/2026-03-02_Quarterly-review_4b1e9f02.ics   # iCalendar document
  Calendar/2026-03-02_Quarterly-review_4b1e9f02.json  # the sidecar record
  manifest.jsonl                                       # one sidecar per line
```

```py
from office365.migration import MigrationJob
from office365.migration.outlook import CalendarSource, IcsExportTarget

job = MigrationJob(CalendarSource(calendar), IcsExportTarget("./calendar-export"))
job.plan()
job.run()
print(job.verify().summary())
```

The payload is *rendered* from the event record rather than fetched, so the same
event always produces the same bytes and a byte checksum verifies the tree —
`verify()` here is exact, not approximate.

Deliberate choices, all of them visible in the sidecar:

- **One item per series, not per occurrence.** A recurring event exports as its
  series master (an `RRULE` plus Graph's `recurrence` object), because importing
  both the series and its instances would duplicate the meeting.
  `--instances` overrides that for archival exports.
- **Cancelled events are skipped** (`--cancelled` includes them): they are
  tombstones, and an import creates live events.
- **HTML bodies ride in `X-ALT-DESC;FMTTYPE=text/html`** — the standard place for
  HTML in `.ics` — instead of being flattened into a lossy plain-text
  `DESCRIPTION`.
- **Time zones are passed through**, a wall clock plus `TZID=Europe/Kiev`, so
  Graph's windows/IANA names travel unchanged and no conversion can drift.
- **Attendees are descriptive.** `ATTENDEE`/`ORGANIZER` lines are written for
  other clients to read; an import recreates them from the sidecar, since Graph
  decides `responseStatus` and `isOrganizer` itself.
