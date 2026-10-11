from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.configurations.ios.home_screen_folder_page import (
    IosHomeScreenFolderPage,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class IosHomeScreenFolder(ClientValue):
    pages: ClientValueCollection[IosHomeScreenFolderPage] = field(
        default_factory=lambda: ClientValueCollection(IosHomeScreenFolderPage)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosHomeScreenFolder"
