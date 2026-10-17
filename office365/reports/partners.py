"""Compatibility import for the canonical ``Partners``.

``microsoft.graph.partners`` is a single Graph entity; the canonical model
lives in :mod:`office365.partners`.
"""

from __future__ import annotations

from office365.partners.partners import Partners

__all__ = ["Partners"]
