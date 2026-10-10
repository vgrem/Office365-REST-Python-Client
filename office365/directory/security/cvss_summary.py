from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.vulnerability_severity import (
        VulnerabilitySeverity,
    )


@dataclass
class CvssSummary(ClientValue):
    score: float | None = None
    vectorString: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.CvssSummary"

    severity: VulnerabilitySeverity = VulnerabilitySeverity.none
