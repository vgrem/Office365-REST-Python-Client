from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.identitygovernance.process_content_metadata_base import (
    ProcessContentMetadataBase,
)
from office365.directory.policies.protected_application_metadata import (
    ProtectedApplicationMetadata,
)
from office365.intune.devices.device_metadata import DeviceMetadata
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.activity_metadata import ActivityMetadata
from office365.security.datasecurity.integrated_application_metadata import (
    IntegratedApplicationMetadata,
)


@dataclass
class ProcessContentRequest(ClientValue):
    contentEntries: ClientValueCollection[ProcessContentMetadataBase] = field(
        default_factory=lambda: ClientValueCollection(ProcessContentMetadataBase)
    )
    deviceMetadata: DeviceMetadata = field(default_factory=DeviceMetadata)
    integratedAppMetadata: IntegratedApplicationMetadata = field(default_factory=IntegratedApplicationMetadata)
    protectedAppMetadata: ProtectedApplicationMetadata = field(default_factory=ProtectedApplicationMetadata)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ProcessContentRequest"

    activityMetadata: ActivityMetadata = field(default_factory=ActivityMetadata)
