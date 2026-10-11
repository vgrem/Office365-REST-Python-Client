from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.file_plan_subcategory import FilePlanSubcategory


@dataclass
class FilePlanAppliedCategory(ClientValue):
    subcategory: FilePlanSubcategory = field(default_factory=FilePlanSubcategory)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.FilePlanAppliedCategory"
