from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.sensitivitylabels.labelactionsource import LabelActionSource
    from office365.security.datasecurity.sensitivity_label import (
        SensitivityLabel,
    )
    from office365.security.datasecurity.usage_rights_included import (
        UsageRightsIncluded,
    )


class SensitivityLabel(Entity):
    """Represents a sensitivity label that defines how to protect and handle content."""

    @property
    def name(self) -> Optional[str]:
        return self.properties.get("name", None)

    @property
    def display_name(self) -> Optional[str]:
        return self.properties.get("displayName", None)

    @property
    def description(self) -> Optional[str]:
        return self.properties.get("description", None)

    @property
    def priority(self) -> Optional[int]:
        return self.properties.get("priority", None)

    @property
    def sensitivity(self) -> Optional[int]:
        return self.properties.get("sensitivity", None)

    @property
    def enabled(self) -> Optional[bool]:
        return self.properties.get("enabled", None)

    @property
    def action_source(self) -> LabelActionSource:
        """Gets the actionSource property"""
        from office365.onedrive.sensitivitylabels.labelactionsource import (
            LabelActionSource,
        )

        return self.properties.get("actionSource", LabelActionSource.manual)

    @property
    def auto_tooltip(self) -> Optional[str]:
        """Gets the autoTooltip property"""
        return self.properties.get("autoTooltip", None)

    @property
    def has_protection(self) -> Optional[bool]:
        """Gets the hasProtection property"""
        return self.properties.get("hasProtection", None)

    @property
    def is_default(self) -> Optional[bool]:
        """Gets the isDefault property"""
        return self.properties.get("isDefault", None)

    @property
    def is_endpoint_protection_enabled(self) -> Optional[bool]:
        """Gets the isEndpointProtectionEnabled property"""
        return self.properties.get("isEndpointProtectionEnabled", None)

    @property
    def is_scoped_to_user(self) -> Optional[bool]:
        """Gets the isScopedToUser property"""
        return self.properties.get("isScopedToUser", None)

    @property
    def locale(self) -> Optional[str]:
        """Gets the locale property"""
        return self.properties.get("locale", None)

    @property
    def tool_tip(self) -> Optional[str]:
        """Gets the toolTip property"""
        return self.properties.get("toolTip", None)

    @property
    def rights(self) -> UsageRightsIncluded:
        """Gets the rights property"""
        from office365.security.datasecurity.usage_rights_included import (
            UsageRightsIncluded,
        )

        return self.properties.get(
            "rights", UsageRightsIncluded(self.context, ResourcePath("rights", self.resource_path))
        )

    @property
    def sublabels(self) -> EntityCollection[SensitivityLabel]:
        """Gets the sublabels property"""
        from office365.security.datasecurity.sensitivity_label import (
            SensitivityLabel,
        )

        return self.properties.get(
            "sublabels",
            EntityCollection[SensitivityLabel](
                self.context, SensitivityLabel, ResourcePath("sublabels", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SensitivityLabel"
