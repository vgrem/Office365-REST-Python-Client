from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class MyGroupsResult(Entity):
    @property
    def entity_type_name(self):
        return "SP.Directory.MyGroupsResult"

    @property
    def has_next(self) -> Optional[bool]:
        """Gets the HasNext property"""
        return self.properties.get("HasNext", None)

    @property
    def has_prev(self) -> Optional[bool]:
        """Gets the HasPrev property"""
        return self.properties.get("HasPrev", None)
