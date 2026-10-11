from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.mobile_app_identifier import MobileAppIdentifier


class ManagedMobileApp(Entity):
    @property
    def mobile_app_identifier(self) -> MobileAppIdentifier:
        """Gets the mobileAppIdentifier property"""
        from office365.intune.devices.management.mobileapps.mobile_app_identifier import MobileAppIdentifier

        return self.properties.get("mobileAppIdentifier", MobileAppIdentifier())

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedMobileApp"
