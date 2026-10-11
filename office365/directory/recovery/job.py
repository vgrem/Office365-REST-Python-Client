from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class RecoveryJob(Entity):
    @property
    def total_failed_changes(self) -> Optional[int]:
        """Gets the totalFailedChanges property"""
        return self.properties.get("totalFailedChanges", None)

    @property
    def total_links_modified(self) -> Optional[int]:
        """Gets the totalLinksModified property"""
        return self.properties.get("totalLinksModified", None)

    @property
    def total_objects_modified(self) -> Optional[int]:
        """Gets the totalObjectsModified property"""
        return self.properties.get("totalObjectsModified", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.entraRecoveryServices.RecoveryJob"
