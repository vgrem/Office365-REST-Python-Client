from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class LocalizedLabel(ClientValue):
    isDefault: bool | None = None
    languageTag: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.termStore.LocalizedLabel"
