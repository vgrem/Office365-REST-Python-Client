from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class DeviceCategory(Entity):
    """
    Device categories provides a way to organize your devices. Using device categories, company administrators
    can define their own categories that make sense to their company. These categories can then be applied
    to a device in the Intune Azure console or selected by a user during device enrollment.
    You can filter reports and create dynamic Azure Active Directory device groups based on device categories.
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
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceCategory"
