from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.sharing.ability_status import SharingAbilityStatus
from office365.sharepoint.sharing.inherited_from import InheritedFrom
from office365.sharepoint.sharing.principal import Principal


@dataclass
class PrincipalInfo(ClientValue):
    canBeModified: SharingAbilityStatus = field(default_factory=SharingAbilityStatus)
    ExpirationDateTimeOnACE: datetime | None = None
    inheritedFrom: InheritedFrom = field(default_factory=InheritedFrom)
    isInherited: bool | None = None
    members: ClientValueCollection[Principal] = field(default_factory=lambda: ClientValueCollection(Principal))
    principal: Principal = field(default_factory=Principal)
    role: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "SP.Sharing.PrincipalInfo"
