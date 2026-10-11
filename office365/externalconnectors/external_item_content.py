from __future__ import annotations

from dataclasses import dataclass

from office365.externalconnectors.itemcontenttype import (
    ExternalItemContentType,
)
from office365.runtime.client_value import ClientValue


@dataclass
class ExternalItemContent(ClientValue):
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.ExternalItemContent"

    type: ExternalItemContentType = ExternalItemContentType.text
