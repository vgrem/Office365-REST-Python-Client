from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.vm_cloud_provider import VmCloudProvider


@dataclass
class VmMetadata(ClientValue):
    resourceId: str | None = None
    subscriptionId: str | None = None
    vmId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.VmMetadata"

    cloudProvider: VmCloudProvider = VmCloudProvider.unknown
