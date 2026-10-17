"""Compatibility import for :class:`office365.directory.synchronization.attribute_mapping.AttributeMapping`.

The class used to be duplicated here with the same members; the canonical model
lives with the rest of the synchronization ``microsoft.graph.attributeMapping`` graph.
"""

from __future__ import annotations

from office365.directory.synchronization.attribute_mapping import AttributeMapping

__all__ = ["AttributeMapping"]
