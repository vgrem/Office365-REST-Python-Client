from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.identities.ip_range import IpRange


class IpNamedLocation(Entity):
    @property
    def ip_ranges(self) -> ClientValueCollection[IpRange]:
        """Gets the ipRanges property"""
        from office365.directory.identities.ip_range import IpRange

        return self.properties.get("ipRanges", ClientValueCollection[IpRange](IpRange))

    @property
    def is_trusted(self) -> Optional[bool]:
        """Gets the isTrusted property"""
        return self.properties.get("isTrusted", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IpNamedLocation"
