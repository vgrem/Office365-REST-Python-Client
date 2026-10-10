from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from office365.communications.teleconference_device_media_quality import (
    TeleconferenceDeviceMediaQuality,
)
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class TeleconferenceDeviceQuality(ClientValue):
    """ """

    callChainId: UUID | None = None

    cloudServiceDeploymentEnvironment: str | None = None

    cloudServiceDeploymentId: str | None = None

    cloudServiceInstanceName: str | None = None

    cloudServiceName: str | None = None

    deviceDescription: str | None = None

    deviceName: str | None = None

    mediaLegId: UUID | None = None

    mediaQualityList: ClientValueCollection[TeleconferenceDeviceMediaQuality] = field(
        default_factory=lambda: ClientValueCollection(TeleconferenceDeviceMediaQuality)
    )

    participantId: UUID | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeleconferenceDeviceQuality"
