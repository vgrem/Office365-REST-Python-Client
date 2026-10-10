from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ImageInfo(ClientValue):
    addImageQuery: bool | None = None
    alternateText: str | None = None
    alternativeText: str | None = None
    iconUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ImageInfo"
