from __future__ import annotations

from enum import Enum


class CustomCalloutExtensionType(Enum):
    preApproval = "0"
    postApproval = "1"
    grant = "2"
    revoke = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomCalloutExtensionType"
