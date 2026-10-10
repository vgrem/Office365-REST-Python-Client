from __future__ import annotations

from typing import Optional

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class MembersInfo(Entity):
    @property
    def entity_type_name(self):
        return "SP.Directory.MembersInfo"

    @property
    def member_names(self) -> StringCollection:
        """Gets the MemberNames property"""
        return self.properties.get("MemberNames", StringCollection())

    @property
    def total_count(self) -> Optional[int]:
        """Gets the TotalCount property"""
        return self.properties.get("TotalCount", None)
