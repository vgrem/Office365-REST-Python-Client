from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.entity import Entity


@dataclass
class SearchHit(ClientValue):
    contentSource: str | None = None
    hitId: str | None = None
    isCollapsed: bool | None = None
    rank: int | None = None
    resultTemplateId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchHit"

    summary: str | None = None

    resource: Entity | None = None
