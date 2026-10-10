from __future__ import annotations

from enum import Enum


class WindowsInformationProtectionPinCharacterRequirements(Enum):
    notAllow = "0"
    requireAtLeastOne = "1"
    allow = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionPinCharacterRequirements"
