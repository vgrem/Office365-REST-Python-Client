from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class SPMigrationJobStatus(Entity):
    """"""

    @property
    def job_id(self) -> Optional[UUID]:
        """Gets the JobId property"""
        return self.properties.get("JobId", None)

    @property
    def job_state(self) -> Optional[int]:
        """Gets the JobState property"""
        return self.properties.get("JobState", None)
