from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ManagedAppDiagnosticStatus(ClientValue):
    """Represents diagnostics status"""

    mitigationInstruction: str | None = None

    state: str | None = None

    validationName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedAppDiagnosticStatus"
