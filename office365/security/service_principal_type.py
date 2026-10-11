from __future__ import annotations

from enum import Enum


class ServicePrincipalType(Enum):
    unknown = "0"
    application = "1"
    managedIdentity = "2"
    legacy = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.ServicePrincipalType"
