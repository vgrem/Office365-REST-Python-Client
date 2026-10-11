from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.public_error import PublicError


@dataclass
class PublicErrorResponse(ClientValue):
    error: PublicError = field(default_factory=PublicError)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PublicErrorResponse"
