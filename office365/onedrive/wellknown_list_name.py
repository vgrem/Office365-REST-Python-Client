"""Compatibility import for the canonical ``WellknownListName``.

``microsoft.graph.wellknownListName`` is a single Graph enum; the canonical
model lives with the To Do lists.
"""

from __future__ import annotations

from office365.todo.tasks.wellknownlistname import WellknownListName

__all__ = ["WellknownListName"]
