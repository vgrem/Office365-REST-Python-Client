"""Compatibility import for the canonical ``TeamsAsyncOperationType``.

``microsoft.graph.teamsAsyncOperationType`` is a single Graph enum; the
canonical model lives next to the async operations. Graph serializes the member
*name* (``cloneTeam``), so the surviving model carries names rather than the
CSDL ordinals.
"""

from __future__ import annotations

from office365.teams.operations.type import TeamsAsyncOperationType

__all__ = ["TeamsAsyncOperationType"]
