"""Outlook (mail) migration product: mailbox assessment + mail export adapters.

Reuses the shared assessment model (containers, scans, reports, export); the
product-specific parts are the mailbox walker (:class:`MailboxAssessor`) with its
scanners (e.g. the ``MailFolders`` folder inventory), and the export adapters
(:class:`MailFolderSource` -> :class:`MailExportTarget`, a portable EML tree).
"""

from office365.migration.outlook.adapters import MANIFEST_NAME, MailExportTarget, MailFolderSource
from office365.migration.outlook.assessor import MailboxAssessor
from office365.migration.outlook.models import MailExportOptions, mail_dest_path, mail_envelope, mail_slug
from office365.migration.outlook.registry import OUTLOOK_SCANS, outlook_scan_pairs
from office365.migration.outlook.scanner import MailboxFolderRecord, MailboxFolderScan, MailFolderData, OutlookOptions

__all__ = [
    "MANIFEST_NAME",
    "OUTLOOK_SCANS",
    "MailExportOptions",
    "MailExportTarget",
    "MailFolderData",
    "MailFolderSource",
    "MailboxAssessor",
    "MailboxFolderRecord",
    "MailboxFolderScan",
    "OutlookOptions",
    "mail_dest_path",
    "mail_envelope",
    "mail_slug",
    "outlook_scan_pairs",
]
