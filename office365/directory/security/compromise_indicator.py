from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.verdict_category import VerdictCategory


@dataclass
class CompromiseIndicator(ClientValue):
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CompromiseIndicator"

    verdict: VerdictCategory = VerdictCategory.none
