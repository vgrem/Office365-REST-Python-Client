from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.sensitivitylabels.usagerights import UsageRights
    from office365.security.datasecurity.sensitivity_label import (
        SensitivityLabel,
    )


class LabelContentRight(Entity):
    @property
    def cid(self) -> Optional[str]:
        """Gets the cid property"""
        return self.properties.get("cid", None)

    @property
    def format(self) -> Optional[str]:
        """Gets the format property"""
        return self.properties.get("format", None)

    @property
    def rights(self) -> UsageRights:
        """Gets the rights property"""
        from office365.onedrive.sensitivitylabels.usagerights import UsageRights

        return self.properties.get("rights", UsageRights.unknown)

    @property
    def label(self) -> SensitivityLabel:
        """Gets the label property"""
        from office365.security.datasecurity.sensitivity_label import (
            SensitivityLabel,
        )

        return self.properties.get("label", SensitivityLabel(self.context, ResourcePath("label", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.LabelContentRight"
