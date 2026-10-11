from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.objects.object import DirectoryObject
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.groups.setting_template_value import SettingTemplateValue


class GroupSettingTemplate(DirectoryObject):
    """Group setting templates represent system-defined settings available to the tenant. Group settings can be
    created based on the available groupSettingTemplates, and values changed from their preset defaults.
    """

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def values(self) -> ClientValueCollection[SettingTemplateValue]:
        """Gets the values property"""
        from office365.directory.groups.setting_template_value import (
            SettingTemplateValue,
        )

        return self.properties.get("values", ClientValueCollection[SettingTemplateValue](SettingTemplateValue))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.GroupSettingTemplate"
