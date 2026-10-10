from __future__ import annotations

from dataclasses import dataclass, field

from office365.onedrive.columns.display_name_localization import DisplayNameLocalization
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ProfileCardAnnotation(ClientValue):
    displayName: str | None = None
    localizations: ClientValueCollection[DisplayNameLocalization] = field(
        default_factory=lambda: ClientValueCollection(DisplayNameLocalization)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProfileCardAnnotation"
