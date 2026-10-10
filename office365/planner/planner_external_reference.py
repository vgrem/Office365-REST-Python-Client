from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class PlannerExternalReference(ClientValue):
    alias: str | None = None
    lastModifiedBy: IdentitySet = field(default_factory=IdentitySet)
    lastModifiedDateTime: datetime | None = None
    previewPriority: str | None = None
    type: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlannerExternalReference"
