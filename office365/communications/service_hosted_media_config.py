from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.media_info import MediaInfo
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class ServiceHostedMediaConfig(ClientValue):
    preFetchMedia: ClientValueCollection[MediaInfo] = field(default_factory=lambda: ClientValueCollection(MediaInfo))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ServiceHostedMediaConfig"
