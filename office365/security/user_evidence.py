from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.stream import Stream
from office365.security.user_account import UserAccount


@dataclass
class UserEvidence(ClientValue):
    stream: Stream = field(default_factory=Stream)
    userAccount: UserAccount = field(default_factory=UserAccount)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.UserEvidence"
