# Import an EML or ICS tree

Put a portable EML or ICS tree back into a mailbox or a calendar — the inverse of
[`migration/export`](../export/README.md). Part of the [Outlook tour](../../README.md).

| What | File | Notes |
|------|------|-------|
| EML tree → mailbox | [`import_folder_eml.py`](./import_folder_eml.py) | `--source`, `--folder`, `--root-name`, `--no-read-state`, `--no-categories` |
| ICS tree → calendar | [`import_calendar_ics.py`](./import_calendar_ics.py) | `--source`, `--calendar`, `--attendees`, `--no-categories` |

```bash
uv run python examples/outlook/migration/import/import_folder_eml.py \
  --source /tmp/mail-export \
  --folder inbox
```

```py
from office365.migration import MigrationJob
from office365.migration.outlook import EmlTreeSource, MailImportOptions, MailboxTarget

job = MigrationJob(EmlTreeSource("./mailbox-export"), MailboxTarget(folder, MailImportOptions()))
job.plan()
job.run()
print(job.verify().summary())
```

## What the import restores

- **The message.** Graph's MIME import takes the RFC 822 bytes as-is (base64 in the
  request body), so headers, HTML and plain bodies, inline images and attachments
  need no field mapping.
- **The folder chain.** The export's top directory *is* the target folder; every
  directory below it is created under the target, using the sidecar's
  `folder_display_path` so `All Mail` does not come back as `All-Mail`.
  `--root-name` nests the whole tree one level deeper.
- **Flags MIME does not carry** — read state, Outlook categories, importance. Those
  cost one extra `PATCH` per message, and only when Exchange's default differs from
  the exported value (`--no-read-state`, `--no-categories` turn it off).
- **Idempotency.** `MailboxTarget.exists()` matches on `internetMessageId` inside the
  target folder, so a re-run — after a throttle, a crash, or with more mail added to
  the tree — skips what is already there instead of duplicating it.

## What it cannot restore (Exchange's limits, not the adapter's)

- **An imported message is a draft.** Graph creates it with `isDraft: true`, and a
  `PATCH` that tries to clear it is silently ignored; only a real delivery (the
  Exchange migration service, IMAP `APPEND`) produces a non-draft. Accept drafts as
  drafts, or use the migration service for a mailbox-wide move.
- **`receivedDateTime` is the import time.** The original date survives in the
  `Date` header, which Graph exposes as `sentDateTime`, and it is restored for free.
- **Timestamps are not restorable**, so `preserve_timestamps` is refused by the
  runner up front rather than silently dropped.
- **4 MB per message.** Graph's MIME import has a 4 MB request cap — a larger
  message needs an upload session, which this target does not use, so it raises
  instead of truncating.

## Verification is semantic, not byte-for-byte

Exchange re-serializes every message it stores (it reflows `Content-Type`, drops
per-part `MIME-Version`, rewrites the `Date` format, adds a `<meta>` tag to HTML), so
an imported message is never byte-identical to the file. `verify()` therefore
compares a **digest** — semantic headers plus a hash of every decoded body/attachment
part — which is stable across that rewrite and still catches a changed body, a
dropped attachment or a different subject:

```py
from office365.migration.outlook import mime_digest

mime_digest(Path("m1.eml").read_bytes()) == mime_digest(message.get_content().execute_query().value)  # True
```

## Calendar → ICS tree

```bash
uv run python examples/outlook/migration/import/import_calendar_ics.py \
  --source ./calendar-export \
  --attendees            # optional: replay invitations (sends real ones)
```

```py
from office365.migration import MigrationJob
from office365.migration.outlook import CalendarImportOptions, CalendarTarget, IcsTreeSource

options = CalendarImportOptions()  # one object, shared by both adapters
job = MigrationJob(IcsTreeSource("./calendar-export", options), CalendarTarget(calendar, options))
job.plan()
job.run()
print(job.verify().summary())
```

## What the calendar import restores

- **The event.** Time range and zone, subject, body (plain or HTML), location,
  show-as, sensitivity, importance, the reminder and Outlook categories are all
  replayed from the sidecar, and a series is recreated as a `seriesMaster` with
  Graph's own `recurrence` object.
- **Idempotency.** A created event comes back with `iCalUid: null` and a fresh Graph
  id, so the target matches on `(subject, wall clock, zone)`: a re-run skips what it
  already created, and two source events that share all three are both imported.
- **A deterministic `transactionId`** — two concurrent runs collide on the server
  instead of both writing, and a collision is adopted, because the event the other
  run created is the work.

## What it cannot restore

- **Attendees are dropped by default.** Creating an event with attendees makes
  Exchange send a real invitation to each of them, and `responseRequested: false`
  does not suppress it (measured) — so an import would mail every invitee of every
  meeting in the tree. `--attendees` opts in; the run otherwise reports how many
  attendee entries it left out.
- **Exchange owns the meeting metadata** — `iCalUid`, the organizer, per-attendee
  responses and the created/modified times are assigned by the service, and the
  signed-in user becomes the organizer.
- **The body is re-serialized** (Exchange wraps it in its own `<html><head><style>…`),
  so verification is a digest of the restorable fields, not the `.ics` bytes. The
  digest read asks for the *source's* timezone (`Prefer: outlook.timezone`), because
  Exchange otherwise renders times in the signed-in mailbox's zone and a migration
  into a mailbox set to another zone would report every event as a mismatch while
  the instants were identical.

## When this is the wrong tool

- **PST / journaling / compliance capture.** Those are Exchange/eDiscovery surfaces;
  a REST client cannot produce or consume a `.pst`.
- **Tenant-wide bulk mailbox moves.** That is the Exchange migration service's job,
  and it works from exactly this EML tree (or an IMAP source) with server-side
  throughput this client cannot match.
- **Dual-write co-existence** (GWSMO and friends). Sync is a service with a scheduler,
  not a one-shot job.
