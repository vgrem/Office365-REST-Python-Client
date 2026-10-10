from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.media_info import MediaInfo
from office365.runtime.client_value import ClientValue


@dataclass
class MediaPrompt(ClientValue):
    mediaInfo: MediaInfo = field(default_factory=MediaInfo)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MediaPrompt"
