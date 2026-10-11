from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class CloudVideoInteropInfo(ClientValue):
    moreInfoWebUrl: str | None = None
    tenantKey: str | None = None
    videoTeleconferenceId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudVideoInteropInfo"
