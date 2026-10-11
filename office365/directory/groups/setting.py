from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.runtime.types.setting_value import SettingValue


class GroupSetting(Entity):
    """Group settings control behaviors such as blocked word lists for group display names or whether guest users are
    allowed to be group owners."""

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def template_id(self) -> Optional[str]:
        """Gets the templateId property"""
        return self.properties.get("templateId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.GroupSetting"

    @property
    def values(self) -> ClientValueCollection[SettingValue]:
        """Gets the values property"""
        from office365.runtime.types.setting_value import SettingValue

        return self.properties.get("values", ClientValueCollection[SettingValue](SettingValue))
