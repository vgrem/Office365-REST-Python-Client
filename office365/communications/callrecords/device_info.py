from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class DeviceInfo(ClientValue):
    captureDeviceDriver: str | None = None
    captureDeviceName: str | None = None
    captureNotFunctioningEventRatio: float | None = None
    cpuInsufficentEventRatio: float | None = None
    deviceClippingEventRatio: float | None = None
    deviceGlitchEventRatio: float | None = None
    howlingEventCount: int | None = None
    initialSignalLevelRootMeanSquare: float | None = None
    lowSpeechLevelEventRatio: float | None = None
    lowSpeechToNoiseEventRatio: float | None = None
    micGlitchRate: float | None = None
    receivedNoiseLevel: int | None = None
    receivedSignalLevel: int | None = None
    renderDeviceDriver: str | None = None
    renderDeviceName: str | None = None
    renderMuteEventRatio: float | None = None
    renderNotFunctioningEventRatio: float | None = None
    renderZeroVolumeEventRatio: float | None = None
    sentNoiseLevel: int | None = None
    sentSignalLevel: int | None = None
    speakerGlitchRate: float | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.DeviceInfo"
