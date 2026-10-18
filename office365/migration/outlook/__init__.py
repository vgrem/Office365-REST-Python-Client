"""Outlook migration product: mailbox assessment, mail export/import, calendar export.

Reuses the shared assessment model (containers, scans, reports, export); the
product-specific parts are the mailbox walker (:class:`MailboxAssessor`) with its
scanners (e.g. the ``MailFolders`` folder inventory), and the adapters that move a
mailbox through a portable EML tree: :class:`MailFolderSource` ->
:class:`MailExportTarget` on the way out, :class:`EmlTreeSource` ->
:class:`MailboxTarget` on the way back in.
"""

from office365.migration.outlook.adapters import MANIFEST_NAME, MailExportTarget, MailFolderSource
from office365.migration.outlook.assessor import MailboxAssessor
from office365.migration.outlook.calendar_adapters import CalendarSource, IcsExportTarget
from office365.migration.outlook.calendar_models import (
    EVENT_COLUMNS,
    CalendarExportOptions,
    event_dest_path,
    event_envelope,
    event_ics,
    event_key,
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
    "EVENT_COLUMNS",
    "MANIFEST_NAME",
    "OUTLOOK_SCANS",
    "CalendarExportOptions",
    "CalendarSource",
    "EmlTreeSource",
    "IcsExportTarget",
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
    "event_dest_path",
    "event_envelope",
    "event_ics",
    "event_key",
    "mail_dest_path",
    "mail_envelope",
    "mail_slug",
    "mime_digest",
    "outlook_scan_pairs",
]
