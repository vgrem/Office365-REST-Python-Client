from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class AnswerKeyword(ClientValue):
    keywords: StringCollection = field(default_factory=StringCollection)
    matchSimilarKeywords: bool | None = None
    reservedKeywords: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.search.AnswerKeyword"
