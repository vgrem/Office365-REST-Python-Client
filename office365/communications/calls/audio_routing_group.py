from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.communications.calls.routingmode import RoutingMode


class AudioRoutingGroup(Entity):
    @property
    def receivers(self) -> StringCollection:
        """Gets the receivers property"""
        return self.properties.get("receivers", StringCollection())

    @property
    def routing_mode(self) -> RoutingMode:
        """Gets the routingMode property"""
        from office365.communications.calls.routingmode import RoutingMode

        return self.properties.get("routingMode", RoutingMode.oneToOne)

    @property
    def sources(self) -> StringCollection:
        """Gets the sources property"""
        return self.properties.get("sources", StringCollection())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AudioRoutingGroup"
