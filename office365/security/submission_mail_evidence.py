from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class SubmissionMailEvidence(ClientValue):
    networkMessageId: str | None = None
    recipient: str | None = None
    reportType: str | None = None
    sender: str | None = None
    senderIp: str | None = None
    subject: str | None = None
    submissionDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    submissionId: str | None = None
    submitter: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.SubmissionMailEvidence"
