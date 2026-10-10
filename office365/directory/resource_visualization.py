from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ResourceVisualization(ClientValue):
    containerDisplayName: str | None = None
    containerType: str | None = None
    containerWebUrl: str | None = None
    mediaType: str | None = None
    previewImageUrl: str | None = None
    previewText: str | None = None
    title: str | None = None
    type: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ResourceVisualization"
