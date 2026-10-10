from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AlteredQueryToken(ClientValue):
    length: int | None = None
    offset: int | None = None
    suggestion: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AlteredQueryToken"
