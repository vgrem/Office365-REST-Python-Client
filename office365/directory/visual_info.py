from __future__ import annotations

from dataclasses import dataclass, field

from office365.common.image_info import ImageInfo
from office365.runtime.client_value import ClientValue
from office365.runtime.types.json import Json


@dataclass
class VisualInfo(ClientValue):
    attribution: ImageInfo = field(default_factory=ImageInfo)
    backgroundColor: str | None = None
    content: Json = field(default_factory=Json)
    description: str | None = None
    displayText: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VisualInfo"
