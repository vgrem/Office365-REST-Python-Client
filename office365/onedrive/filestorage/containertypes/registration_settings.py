from __future__ import annotations

from dataclasses import dataclass

from office365.admin.sharepoint.sharingcapabilities import SharingCapabilities
from office365.runtime.client_value import ClientValue


@dataclass
class FileStorageContainerTypeRegistrationSettings(ClientValue):
    isDiscoverabilityEnabled: bool | None = None
    isItemVersioningEnabled: bool | None = None
    isSearchEnabled: bool | None = None
    isSharingRestricted: bool | None = None
    itemMajorVersionLimit: int | None = None
    maxStoragePerContainerInBytes: int | None = None
    sharingCapability: SharingCapabilities = SharingCapabilities.disabled
    urlTemplate: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FileStorageContainerTypeRegistrationSettings"
