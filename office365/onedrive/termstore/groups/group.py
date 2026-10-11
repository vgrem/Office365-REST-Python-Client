from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.onedrive.termstore.sets.collection import SetCollection
from office365.onedrive.termstore.sets.set import Set
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.termstore.groups.scope import TermGroupScope


class Group(Entity):
    """Term Group"""

    def ensure_set(self, name: str) -> Set:
        """Gets existing set by name or creates a new one (idempotent)."""
        return self.sets.ensure_set(name)

    def delete_object(self, *, ignore_missing: bool = False) -> Self:
        def _delete_group():
            super(Group, self).delete_object(ignore_missing=ignore_missing)

        def _on_sets_loaded(sets: SetCollection):
            if len(sets) == 0:
                _delete_group()
            else:
                for s in sets:
                    s.delete_object(ignore_missing=ignore_missing)
                self.after_execute(lambda _: _delete_group())

        self.sets.get().after_execute(_on_sets_loaded)
        return self

    def __str__(self) -> str:
        return self.display_name or ""

    @property
    def display_name(self) -> str | None:
        """Name of the group."""
        return self.properties.get("displayName", None)

    @property
    def parent_site_id(self) -> str | None:
        """ID of the parent site of this group."""
        return self.properties.get("parentSiteId", None)

    @property
    def sets(self) -> SetCollection:
        """Collection of all sets available in the term store."""
        return self.properties.get(
            "sets",
            SetCollection(self.context, ResourcePath("sets", self.resource_path), self),
        )

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def scope(self) -> TermGroupScope:
        """Gets the scope property"""
        from office365.onedrive.termstore.groups.scope import TermGroupScope

        return self.properties.get("scope", TermGroupScope.global_)
