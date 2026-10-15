"""Source→target identity maps for a migration.

A migration that recreates structure cannot assume the platform preserves the
identifiers read from the source: SharePoint Online assigns a **list content
type** a fresh ``StringId`` when it is recreated over REST, yet every list item
keeps carrying the *source* identifier in its ``ContentTypeId`` column. Writing
that identifier verbatim either fails or silently lands the item under the wrong
content type.

:class:`ContentTypeMap` records the source→target content-type identity (matched
by name — the only stable key across a REST recreate) so the item projection can
rewrite ``ContentTypeId`` before it is written. It is a plain dict of source id →
target id, so it stays JSON-friendly and can be persisted or rebuilt.

This is the first piece of the migration map layer. Other maps (list/field GUIDs
for cross-list lookups, a term-store map, a cross-tenant user map) are added when
they have a consumer: the same-tenant path needs none of them, because the term
store and user identities are tenant-wide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional

__all__ = ["ContentTypeMap"]


@dataclass
class ContentTypeMap:
    """Source content-type identifier → target content-type identifier.

    Records only the identifiers that actually differ; a content type the target
    already exposes (or that is not recreated) is left out and :meth:`resolve`
    returns its source id unchanged.
    """

    entries: Dict[str, str] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.entries)

    def resolve(self, source_id: Optional[str]) -> Optional[str]:
        """The target identifier for ``source_id`` (unchanged when unmapped)."""
        if not source_id:
            return source_id
        return self.entries.get(source_id, source_id)

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Return a JSON-friendly ``{"entries": {...}}`` dict."""
        return {"entries": dict(self.entries)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContentTypeMap":
        """Rebuild a map from :meth:`to_dict` output."""
        return cls(entries=dict(data.get("entries") or {}))

    @classmethod
    def build(cls, source: Iterable[Any], target: Iterable[Any]) -> "ContentTypeMap":
        """Build the map from source and target content types, matched by name.

        Both sequences may hold any objects exposing ``name`` and ``string_id``
        (a captured
        :class:`~office365.migration.sharepoint.structure.ContentTypeDefinition`
        or a live ``ContentType``). Only identifiers that differ are stored.
        """

        def by_name(items: Iterable[Any]) -> Dict[str, str]:
            result: Dict[str, str] = {}
            for item in items:
                name = getattr(item, "name", None)
                string_id = getattr(item, "string_id", None)
                if name and string_id and name not in result:
                    result[name] = string_id
            return result

        source_by_name = by_name(source)
        target_by_name = by_name(target)
        entries = {
            source_id: target_by_name[name]
            for name, source_id in source_by_name.items()
            if name in target_by_name and target_by_name[name] != source_id
        }
        return cls(entries)
