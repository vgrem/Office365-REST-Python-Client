from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ChallengingWord(ClientValue):
    count: int | None = None
    word: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChallengingWord"
