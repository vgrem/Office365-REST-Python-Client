from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.configurations.ios.home_screen_item import (
    IosHomeScreenItem,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class IosHomeScreenPage(ClientValue):
    displayName: str | None = None
    icons: ClientValueCollection[IosHomeScreenItem] = field(
        default_factory=lambda: ClientValueCollection(IosHomeScreenItem)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosHomeScreenPage"
