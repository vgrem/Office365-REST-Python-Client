"""Outlook migration product: mailbox assessment, mail, calendar and contacts export/import.

Reuses the shared assessment model (containers, scans, reports, export); the
product-specific parts are the mailbox walker (:class:`MailboxAssessor`) with its
scanners (e.g. the ``MailFolders`` folder inventory), and the adapters that move a
mailbox through a portable EML tree: :class:`MailFolderSource` ->
:class:`MailExportTarget` on the way out, :class:`EmlTreeSource` ->
:class:`MailboxTarget` on the way back in. A calendar does the same with an ICS
sidecar tree: :class:`CalendarSource` -> :class:`IcsExportTarget`, and
:class:`IcsTreeSource` -> :class:`CalendarTarget`. Contacts do the same with a vCard
sidecar tree: :class:`ContactSource` -> :class:`VcfExportTarget`, and
:class:`VcfTreeSource` -> :class:`ContactTarget`.
"""

from office365.migration.outlook.adapters import MANIFEST_NAME, MailExportTarget, MailFolderSource
from office365.migration.outlook.assessor import MailboxAssessor
from office365.migration.outlook.calendar_adapters import (
    CalendarSource,
    CalendarTarget,
    IcsExportTarget,
    IcsTreeSource,
)
from office365.migration.outlook.calendar_models import (
    EVENT_COLUMNS,
    CalendarExportOptions,
    CalendarImportOptions,
    event_create_payload,
    event_dedup_key,
    event_dest_path,
    event_digest,
    event_dropped_attendees,
    event_envelope,
    event_ics,
    event_key,
    event_transaction_id,
)
from office365.migration.outlook.contacts_adapters import (
    ContactSource,
    ContactTarget,
    VcfExportTarget,
    VcfTreeSource,
)
from office365.migration.outlook.contacts_models import (
    CONTACT_COLUMNS,
    ContactExportOptions,
    ContactImportOptions,
    ContactRecord,
)
from office365.migration.outlook.eml_import import EmlTreeSource, MailboxTarget
from office365.migration.outlook.models import (
    MailExportOptions,
    MailImportOptions,
    mail_dest_path,
    mail_envelope,
    mail_slug,
    mime_digest,
)
from office365.migration.outlook.registry import OUTLOOK_SCANS, outlook_scan_pairs
from office365.migration.outlook.scanner import MailboxFolderRecord, MailboxFolderScan, MailFolderData, OutlookOptions

__all__ = [
    "CONTACT_COLUMNS",
    "EVENT_COLUMNS",
    "MANIFEST_NAME",
    "OUTLOOK_SCANS",
    "CalendarExportOptions",
    "CalendarImportOptions",
    "CalendarSource",
    "CalendarTarget",
    "ContactExportOptions",
    "ContactImportOptions",
    "ContactRecord",
    "ContactSource",
    "ContactTarget",
    "EmlTreeSource",
    "IcsExportTarget",
    "IcsTreeSource",
    "MailExportOptions",
    "MailExportTarget",
    "MailFolderData",
    "MailFolderSource",
    "MailImportOptions",
    "MailboxAssessor",
    "MailboxFolderRecord",
    "MailboxFolderScan",
    "MailboxTarget",
    "OutlookOptions",
    "VcfExportTarget",
    "VcfTreeSource",
    "event_create_payload",
    "event_dedup_key",
    "event_dest_path",
    "event_digest",
    "event_dropped_attendees",
    "event_envelope",
    "event_ics",
    "event_key",
    "event_transaction_id",
    "mail_dest_path",
    "mail_envelope",
    "mail_slug",
    "mime_digest",
    "outlook_scan_pairs",
]
