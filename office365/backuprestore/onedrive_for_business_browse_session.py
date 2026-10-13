from __future__ import annotations

from typing import Optional

from office365.backuprestore.browse_session_base import BrowseSessionBase


class OneDriveForBusinessBrowseSession(BrowseSessionBase):
    @property
    def directory_object_id(self) -> Optional[str]:
        """Gets the directoryObjectId property"""
        return self.properties.get("directoryObjectId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OneDriveForBusinessBrowseSession"
