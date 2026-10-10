from __future__ import annotations

from enum import Enum


class ChannelLayoutType(Enum):
    post = "0"
    chat = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChannelLayoutType"
