"""Settings that configure the behavior of a SharePoint Embedded container type.

Most settings can be overridden at the container level by the consuming tenant.

https://learn.microsoft.com/en-us/graph/api/resources/filestoragecontainertypesettings
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from office365.admin.sharepoint.sharingcapabilities import SharingCapabilities
from office365.runtime.client_value import ClientValue


@dataclass
class FileStorageContainerTypeSettings(ClientValue):
    """Configuration options for a container type.

    Fields:
        isDiscoverabilityEnabled: Whether containers of this type appear in search
            and the SharePoint Embedded app catalog.
        isSearchEnabled: Whether content in containers of this type is searchable.
        isItemVersioningEnabled: Whether version history is enabled for items.
        itemMajorVersionLimit: Maximum number of major versions retained.
        maxStoragePerContainerInBytes: Maximum storage per container in bytes.
        isSharingRestricted: Whether sharing outside the organization is restricted.
        consumingTenantOverridables: Comma-separated list of settings that consuming
            tenants can override (e.g. "isSearchEnabled,itemMajorVersionLimit").
        urlTemplate: URL template for generating container-specific URLs.
    """

    isDiscoverabilityEnabled: Optional[bool] = None
    isSearchEnabled: Optional[bool] = None
    isItemVersioningEnabled: Optional[bool] = None
    itemMajorVersionLimit: Optional[int] = None
    maxStoragePerContainerInBytes: Optional[int] = None
    isSharingRestricted: Optional[bool] = None
    consumingTenantOverridables: Optional[str] = None
    urlTemplate: Optional[str] = None
    sharingCapability: SharingCapabilities = SharingCapabilities.disabled

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FileStorageContainerTypeSettings"
