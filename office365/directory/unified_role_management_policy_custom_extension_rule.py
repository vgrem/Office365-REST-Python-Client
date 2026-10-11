from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class UnifiedRoleManagementPolicyCustomExtensionRule(Entity):
    @property
    def custom_attributes(self) -> StringCollection:
        """Gets the customAttributes property"""
        return self.properties.get("customAttributes", StringCollection())

    @property
    def custom_extension_id(self) -> Optional[str]:
        """Gets the customExtensionId property"""
        return self.properties.get("customExtensionId", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleManagementPolicyCustomExtensionRule"
