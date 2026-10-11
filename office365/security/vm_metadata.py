from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.vm_cloud_provider import VmCloudProvider


@dataclass
class VmMetadata(ClientValue):
    resourceId: str | None = None
    subscriptionId: str | None = None
    vmId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.VmMetadata"

    cloudProvider: VmCloudProvider = VmCloudProvider.unknown
