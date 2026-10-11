from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.resource_access_event import ResourceAccessEvent


@dataclass
class UserAccount(ClientValue):
    accountName: str | None = None
    activeDirectoryObjectGuid: UUID | None = None
    azureAdUserId: str | None = None
    displayName: str | None = None
    domainName: str | None = None
    resourceAccessEvents: ClientValueCollection[ResourceAccessEvent] = field(
        default_factory=lambda: ClientValueCollection(ResourceAccessEvent)
    )
    tenantId: str | None = None
    userPrincipalName: str | None = None
    userSid: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.UserAccount"
