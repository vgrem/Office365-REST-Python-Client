from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class FlowSynchronizationResult(Entity):
    @property
    def synchronization_data(self) -> Optional[str]:
        """Gets the SynchronizationData property"""
        return self.properties.get("SynchronizationData", None)

    @property
    def synchronization_status(self) -> Optional[int]:
        """Gets the SynchronizationStatus property"""
        return self.properties.get("SynchronizationStatus", None)
