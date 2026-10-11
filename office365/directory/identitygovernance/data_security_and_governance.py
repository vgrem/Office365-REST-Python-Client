from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.datasecurity.sensitivity_label import (
        SensitivityLabel,
    )


class DataSecurityAndGovernance(Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DataSecurityAndGovernance"

    @property
    def sensitivity_labels(self) -> EntityCollection[SensitivityLabel]:
        """Gets the sensitivityLabels property"""
        from office365.security.datasecurity.sensitivity_label import (
            SensitivityLabel,
        )

        return self.properties.get(
            "sensitivityLabels",
            EntityCollection[SensitivityLabel](
                self.context, SensitivityLabel, ResourcePath("sensitivityLabels", self.resource_path)
            ),
        )
