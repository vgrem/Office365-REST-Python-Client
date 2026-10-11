from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.user_account import UserAccount


@dataclass
class MailboxEvidence(ClientValue):
    displayName: str | None = None
    primaryAddress: str | None = None
    upn: str | None = None
    userAccount: UserAccount = field(default_factory=UserAccount)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.MailboxEvidence"
