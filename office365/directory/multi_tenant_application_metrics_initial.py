from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class MultiTenantApplicationMetricsInitial(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MultiTenantApplicationMetricsInitial"
