from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.subjectset import SubjectSet
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class UnifiedApprovalStage(ClientValue):
    approvalStageTimeOutInDays: int | None = None
    escalationApprovers: ClientValueCollection[SubjectSet] = field(
        default_factory=lambda: ClientValueCollection(SubjectSet)
    )
    escalationTimeInMinutes: int | None = None
    isApproverJustificationRequired: bool | None = None
    isEscalationEnabled: bool | None = None
    primaryApprovers: ClientValueCollection[SubjectSet] = field(
        default_factory=lambda: ClientValueCollection(SubjectSet)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedApprovalStage"
