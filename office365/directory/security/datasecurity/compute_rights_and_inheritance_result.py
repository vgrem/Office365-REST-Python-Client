from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.directory.security.datasecurity.sensitivity_label import SensitivityLabel
from office365.entity_collection import EntityCollection
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.datasecurity.label_content_right import (
        LabelContentRight,
    )


@dataclass
class ComputeRightsAndInheritanceResult(ClientValue):
    inheritedLabel: SensitivityLabel | None = None
    sensitivityLabels: EntityCollection[SensitivityLabel] | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ComputeRightsAndInheritanceResult"

    contentRights: EntityCollection[LabelContentRight] | None = None
