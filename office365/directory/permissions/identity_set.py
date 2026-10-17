"""Compatibility import for :class:`office365.directory.identity_set.IdentitySet`.

The class used to be duplicated here with the same members; the canonical model
lives next to the rest of the ``microsoft.graph.IdentitySet`` graph.
"""

from __future__ import annotations

from office365.directory.identity_set import IdentitySet

__all__ = ["IdentitySet"]
