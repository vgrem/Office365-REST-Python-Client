from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from office365.directory.security.alerts.antispamteamsdirection import AntispamTeamsDirection
from office365.directory.security.file_evidence import FileEvidence
from office365.directory.security.url_evidence import UrlEvidence
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection


@dataclass
class TeamsMessageEvidence(ClientValue):
    campaignId: str | None = None
    channelId: str | None = None
    files: ClientValueCollection[FileEvidence] = field(default_factory=lambda: ClientValueCollection(FileEvidence))
    groupId: str | None = None
    isExternal: bool | None = None
    isOwned: bool | None = None
    lastModifiedDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    messageDirection: AntispamTeamsDirection = AntispamTeamsDirection.unknown
    messageId: str | None = None
    owningTenantId: UUID | None = None
    parentMessageId: str | None = None
    receivedDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    recipients: StringCollection = field(default_factory=StringCollection)
    senderFromAddress: str | None = None
    senderIP: str | None = None
    sourceAppName: str | None = None
    sourceId: str | None = None
    subject: str | None = None
    suspiciousRecipients: StringCollection = field(default_factory=StringCollection)
    threadId: str | None = None
    threadType: str | None = None
    urls: ClientValueCollection[UrlEvidence] = field(default_factory=lambda: ClientValueCollection(UrlEvidence))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.TeamsMessageEvidence"
