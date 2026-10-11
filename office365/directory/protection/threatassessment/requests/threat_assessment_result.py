from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.protection.threatassessment.resulttype import (
        ThreatAssessmentResultType,
    )


class ThreatAssessmentResult(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def message(self) -> Optional[str]:
        """Gets the message property"""
        return self.properties.get("message", None)

    @property
    def result_type(self) -> ThreatAssessmentResultType:
        """Gets the resultType property"""
        from office365.directory.protection.threatassessment.resulttype import (
            ThreatAssessmentResultType,
        )

        return self.properties.get("resultType", ThreatAssessmentResultType.checkPolicy)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ThreatAssessmentResult"
