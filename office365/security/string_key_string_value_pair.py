from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class StringKeyStringValuePair(ClientValue):
    key: str | None = None
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.StringKeyStringValuePair"
