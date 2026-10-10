from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class CvssSummary(ClientValue):
    score: float | None = None
    vectorString: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CvssSummary"
