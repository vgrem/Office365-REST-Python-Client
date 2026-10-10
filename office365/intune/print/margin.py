from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class PrintMargin(ClientValue):
    bottom: int | None = None
    left: int | None = None
    right: int | None = None
    top: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintMargin"
