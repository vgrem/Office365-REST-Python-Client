from __future__ import annotations

from enum import Enum


class FileStorageContainerTypeSettingsOverride(Enum):
    urlTemplate = "0"
    isDiscoverabilityEnabled = "1"
    isSearchEnabled = "2"
    isItemVersioningEnabled = "3"
    itemMajorVersionLimit = "4"
    maxStoragePerContainerInBytes = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FileStorageContainerTypeSettingsOverride"

    isOfficeRestricted = "7"
