from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class B2BRegistrationMetricsRecent(Entity):
    @property
    def update_date_time(self) -> Optional[datetime]:
        """Gets the updateDateTime property"""
        return self.properties.get("updateDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.B2BRegistrationMetricsRecent"
