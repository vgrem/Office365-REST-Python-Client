from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.mailbox_configuration_type import (
        MailboxConfigurationType,
    )


@dataclass
class MailboxConfigurationEvidence(ClientValue):
    configurationId: str | None = None
    displayName: str | None = None
    externalDirectoryObjectId: UUID | None = None
    mailboxPrimaryAddress: str | None = None
    upn: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.MailboxConfigurationEvidence"

    configurationType: MailboxConfigurationType = MailboxConfigurationType.mailForwardingRule
