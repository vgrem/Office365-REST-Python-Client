from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from office365.communications.callrecords.audio_codec import AudioCodec
from office365.communications.callrecords.media_stream_direction import (
    MediaStreamDirection,
)
from office365.communications.callrecords.modality import Modality
from office365.communications.callrecords.video_codec import VideoCodec
from office365.communications.calls.mediadirection import MediaDirection
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from datetime import timedelta


@dataclass
class MediaStream(ClientValue):
    audioCodec: AudioCodec = AudioCodec.unknown
    averageAudioDegradation: float | None = None
    averageAudioNetworkJitter: timedelta | None = None
    averageBandwidthEstimate: int | None = None
    averageFreezeDuration: timedelta | None = None
    averageJitter: timedelta | None = None
    averagePacketLossRate: float | None = None
    averageRatioOfConcealedSamples: float | None = None
    averageReceivedFrameRate: float | None = None
    averageRoundTripTime: timedelta | None = None
    averageVideoFrameLossPercentage: float | None = None
    averageVideoFrameRate: float | None = None
    averageVideoPacketLossRate: float | None = None
    endDateTime: datetime | None = None
    isAudioForwardErrorCorrectionUsed: bool | None = None
    lowFrameRateRatio: float | None = None
    lowVideoProcessingCapabilityRatio: float | None = None
    maxAudioNetworkJitter: timedelta | None = None
    maxJitter: timedelta | None = None
    maxPacketLossRate: float | None = None
    maxRatioOfConcealedSamples: float | None = None
    maxRoundTripTime: timedelta | None = None
    packetUtilization: int | None = None
    postForwardErrorCorrectionPacketLossRate: float | None = None
    rmsFreezeDuration: timedelta | None = None
    startDateTime: datetime | None = None
    streamDirection: MediaStreamDirection = MediaStreamDirection.callerToCallee
    streamId: str | None = None
    videoCodec: VideoCodec = VideoCodec.unknown
    wasMediaBypassed: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.MediaStream"

    direction: MediaDirection = MediaDirection.inactive

    label: str | None = None

    mediaType: Modality = Modality.audio

    serverMuted: bool | None = None

    sourceId: str | None = None
