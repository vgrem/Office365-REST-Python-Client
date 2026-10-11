from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection
from office365.security.email_sender import EmailSender


@dataclass
class AnalyzedMessageEvidence(ClientValue):
    antiSpamDirection: str | None = None
    attachmentsCount: int | None = None
    deliveryAction: str | None = None
    deliveryLocation: str | None = None
    internetMessageId: str | None = None
    language: str | None = None
    networkMessageId: str | None = None
    receivedDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    recipientEmailAddress: str | None = None
    senderIp: str | None = None
    subject: str | None = None
    threatDetectionMethods: StringCollection = field(default_factory=StringCollection)
    threats: StringCollection = field(default_factory=StringCollection)
    urlCount: int | None = None
    urls: StringCollection = field(default_factory=StringCollection)
    urn: str | None = None
    p1Sender: EmailSender = field(default_factory=EmailSender)
    p2Sender: EmailSender = field(default_factory=EmailSender)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedMessageEvidence"
