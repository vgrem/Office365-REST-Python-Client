from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class MimeContent(ClientValue):
    type: str | None = None
    value: bytes | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MimeContent"
