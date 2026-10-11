from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.virtualevents.presenter_details import (
    VirtualEventPresenterDetails,
)
from office365.runtime.client_value import ClientValue


@dataclass
class VirtualEventPresenterInfo(ClientValue):
    presenterDetails: VirtualEventPresenterDetails = field(default_factory=VirtualEventPresenterDetails)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.VirtualEventPresenterInfo"
