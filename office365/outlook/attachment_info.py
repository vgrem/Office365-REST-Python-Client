"""Compatibility import for the canonical ``AttachmentInfo``.

``microsoft.graph.attachmentInfo`` is a single Graph complex type; the
canonical model lives with the To Do attachments.
"""

from __future__ import annotations

from office365.todo.attachments.info import AttachmentInfo

__all__ = ["AttachmentInfo"]
