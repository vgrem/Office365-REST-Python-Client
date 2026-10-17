"""Compatibility import for :class:`office365.outlook.mail.attachments.type.AttachmentType`.

``microsoft.graph.attachmentType`` is a single Graph enum shared by Outlook and
To Do attachments; the canonical model lives with the Outlook attachments.
"""

from __future__ import annotations

from office365.outlook.mail.attachments.type import AttachmentType

__all__ = ["AttachmentType"]
