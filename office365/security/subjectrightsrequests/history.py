from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.permissions.identity_set import IdentitySet
from office365.directory.privacy.subjectrightsrequeststage import SubjectRightsRequestStage
from office365.directory.privacy.subjectrightsrequeststagestatus import SubjectRightsRequestStageStatus
from office365.runtime.client_value import ClientValue


@dataclass
class SubjectRightsRequestHistory(ClientValue):
    changedBy: IdentitySet = field(default_factory=IdentitySet)
    eventDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    stage: SubjectRightsRequestStage = SubjectRightsRequestStage.contentRetrieval
    stageStatus: SubjectRightsRequestStageStatus = SubjectRightsRequestStageStatus.notStarted
    type: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SubjectRightsRequestHistory"
