from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AutonomousSystem(ClientValue):
    name: str | None = None
    number: int | None = None
    organization: str | None = None
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AutonomousSystem"
