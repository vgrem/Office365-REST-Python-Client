from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.backuprestore.artifactrestorestatus import ArtifactRestoreStatus


class GranularRestoreArtifactBase(Entity):
    @property
    def browse_session_id(self) -> Optional[str]:
        """Gets the browseSessionId property"""
        return self.properties.get("browseSessionId", None)

    @property
    def completion_date_time(self) -> Optional[datetime]:
        """Gets the completionDateTime property"""
        return self.properties.get("completionDateTime", datetime.min)

    @property
    def restored_item_key(self) -> Optional[str]:
        """Gets the restoredItemKey property"""
        return self.properties.get("restoredItemKey", None)

    @property
    def restored_item_path(self) -> Optional[str]:
        """Gets the restoredItemPath property"""
        return self.properties.get("restoredItemPath", None)

    @property
    def restored_item_web_url(self) -> Optional[str]:
        """Gets the restoredItemWebUrl property"""
        return self.properties.get("restoredItemWebUrl", None)

    @property
    def restore_point_date_time(self) -> Optional[datetime]:
        """Gets the restorePointDateTime property"""
        return self.properties.get("restorePointDateTime", datetime.min)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def status(self) -> ArtifactRestoreStatus:
        """Gets the status property"""
        from office365.backuprestore.artifactrestorestatus import ArtifactRestoreStatus

        return self.properties.get("status", ArtifactRestoreStatus.added)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.GranularRestoreArtifactBase"
