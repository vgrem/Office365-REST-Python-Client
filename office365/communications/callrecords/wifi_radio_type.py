from __future__ import annotations

from enum import Enum


class WifiRadioType(Enum):
    unknown = "0"
    wifi80211a = "1"
    wifi80211b = "2"
    wifi80211g = "3"
    wifi80211n = "4"
    wifi80211ac = "5"
    wifi80211ax = "6"
    unknownFutureValue = "7"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.WifiRadioType"
