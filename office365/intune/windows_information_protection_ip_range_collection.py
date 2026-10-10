from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.identities.ip_range import IpRange
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class WindowsInformationProtectionIPRangeCollection(ClientValue):
    displayName: str | None = None
    ranges: ClientValueCollection[IpRange] = field(default_factory=lambda: ClientValueCollection(IpRange))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsInformationProtectionIPRangeCollection"
