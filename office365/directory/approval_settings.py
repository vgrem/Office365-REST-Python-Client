from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.unified_approval_stage import UnifiedApprovalStage
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ApprovalSettings(ClientValue):
    approvalMode: str | None = None
    approvalStages: ClientValueCollection[UnifiedApprovalStage] = field(
        default_factory=lambda: ClientValueCollection(UnifiedApprovalStage)
    )
    isApprovalRequired: bool | None = None
    isApprovalRequiredForExtension: bool | None = None
    isRequestorJustificationRequired: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ApprovalSettings"
