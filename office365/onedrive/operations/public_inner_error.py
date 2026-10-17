"""Compatibility import for the canonical ``PublicInnerError``.

``microsoft.graph.publicInnerError`` is a single Graph complex type; the
canonical model lives in :mod:`office365.runtime.types`.
"""

from __future__ import annotations

from office365.runtime.types.public_inner_error import PublicInnerError

__all__ = ["PublicInnerError"]
