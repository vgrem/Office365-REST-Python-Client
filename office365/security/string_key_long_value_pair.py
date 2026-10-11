from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class StringKeyLongValuePair(ClientValue):
    key: str | None = None
    value: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.StringKeyLongValuePair"
