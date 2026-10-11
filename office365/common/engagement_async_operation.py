from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.teams.viva.engagement.asyncoperationtype import (
        EngagementAsyncOperationType,
    )


class EngagementAsyncOperation(PollableOperation, Entity):
    @property
    def operation_type(self) -> EngagementAsyncOperationType:
        """Gets the operationType property"""
        from office365.teams.viva.engagement.asyncoperationtype import (
            EngagementAsyncOperationType,
        )

        return self.properties.get("operationType", EngagementAsyncOperationType.createCommunity)

    @property
    def resource_id(self) -> Optional[str]:
        """Gets the resourceId property"""
        return self.properties.get("resourceId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EngagementAsyncOperation"
