from __future__ import annotations

from enum import Enum


class ObliterationBehavior(Enum):
    default = "0"
    doNotObliterate = "1"
    obliterateWithWarning = "2"
    always = "3"
    unknownFutureValue = "999"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ObliterationBehavior"
