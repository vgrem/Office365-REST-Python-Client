from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.print.printers.location import PrinterLocation


class PrintConnector(Entity):
    """Represents a print connector that has been registered by using a Universal Print subscription.
    The printConnector resource can be used to view connector status and update properties.
    """

    @property
    def app_version(self) -> Optional[str]:
        """Gets the appVersion property"""
        return self.properties.get("appVersion", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def fully_qualified_domain_name(self) -> Optional[str]:
        """Gets the fullyQualifiedDomainName property"""
        return self.properties.get("fullyQualifiedDomainName", None)

    @property
    def location(self) -> PrinterLocation:
        """Gets the location property"""
        from office365.intune.print.printers.location import PrinterLocation

        return self.properties.get("location", PrinterLocation())

    @property
    def operating_system(self) -> Optional[str]:
        """Gets the operatingSystem property"""
        return self.properties.get("operatingSystem", None)

    @property
    def registered_date_time(self) -> Optional[datetime]:
        """Gets the registeredDateTime property"""
        return self.properties.get("registeredDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrintConnector"
