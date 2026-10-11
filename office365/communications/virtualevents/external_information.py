from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class VirtualEventExternalInformation(ClientValue):
    applicationId: str | None = None
    externalEventId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventExternalInformation"
