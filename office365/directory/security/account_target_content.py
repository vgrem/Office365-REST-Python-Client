from __future__ import annotations

from dataclasses import dataclass

from office365.directory.security.attacksimulations.account_target_content_type import (
    AccountTargetContentType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class AccountTargetContent(ClientValue):
    type: AccountTargetContentType = AccountTargetContentType.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccountTargetContent"
