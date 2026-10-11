from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class DataSubject(ClientValue):
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    residency: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DataSubject"
