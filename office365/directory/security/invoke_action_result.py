from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class InvokeActionResult(ClientValue):
    accountId: str | None = None
    correlationId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.InvokeActionResult"
