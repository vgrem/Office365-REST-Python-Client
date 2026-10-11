from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.security.autonomous_system import AutonomousSystem


class IpAddress(Entity):
    @property
    def country_or_region(self) -> Optional[str]:
        """Gets the countryOrRegion property"""
        return self.properties.get("countryOrRegion", None)

    @property
    def hosting_provider(self) -> Optional[str]:
        """Gets the hostingProvider property"""
        return self.properties.get("hostingProvider", None)

    @property
    def netblock(self) -> Optional[str]:
        """Gets the netblock property"""
        return self.properties.get("netblock", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IpAddress"

    @property
    def autonomous_system(self) -> AutonomousSystem:
        """Gets the autonomousSystem property"""
        from office365.security.autonomous_system import AutonomousSystem

        return self.properties.get("autonomousSystem", AutonomousSystem())
