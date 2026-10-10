from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.identities.provider import IdentityProvider
    from office365.directory.security.action import Action


@dataclass
class InvokeActionResult(ClientValue):
    accountId: str | None = None
    correlationId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.InvokeActionResult"

    action: Action = Action.disable

    identityProvider: IdentityProvider | None = None
