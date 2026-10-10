from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class IosNetworkUsageRule(ClientValue):
    cellularDataBlocked: bool | None = None
    cellularDataBlockWhenRoaming: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosNetworkUsageRule"
