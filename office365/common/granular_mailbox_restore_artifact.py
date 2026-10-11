from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class GranularMailboxRestoreArtifact(Entity):
    @property
    def artifact_count(self) -> Optional[int]:
        """Gets the artifactCount property"""
        return self.properties.get("artifactCount", None)

    @property
    def search_response_id(self) -> Optional[str]:
        """Gets the searchResponseId property"""
        return self.properties.get("searchResponseId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.GranularMailboxRestoreArtifact"
