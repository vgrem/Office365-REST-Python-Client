from __future__ import annotations

from enum import Enum


class AntispamDirectionality(Enum):
    unknown = "0"
    inbound = "1"
    outbound = "2"
    intraOrg = "3"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AntispamDirectionality"
