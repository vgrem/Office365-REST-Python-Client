"""Compatibility import for the canonical ``MeetingChatMode``.

``microsoft.graph.meetingChatMode`` is a single Graph enum; the canonical
model lives with the other ``meeting`` models.
"""

from __future__ import annotations

from office365.communications.meetings.chatmode import MeetingChatMode

__all__ = ["MeetingChatMode"]
