from __future__ import annotations

from enum import Enum


class IdentityProvider(Enum):
    entraID = "1"
    activeDirectory = "2"
    okta = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IdentityProvider"
