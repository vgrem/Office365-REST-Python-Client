"""Compatibility import for the canonical ``TaskFileAttachment``.

``microsoft.graph.taskFileAttachment`` is a single Graph attachment subtype;
the canonical model lives with the To Do attachments.
"""

from __future__ import annotations

from office365.todo.attachments.task_file import TaskFileAttachment

__all__ = ["TaskFileAttachment"]
