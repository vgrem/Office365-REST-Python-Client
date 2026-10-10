from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.connection_item import ConnectionItem


@dataclass
class ExternalItemConfiguration(ClientValue):
    connections: ClientValueCollection[ConnectionItem] = field(
        default_factory=lambda: ClientValueCollection(ConnectionItem)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExternalItemConfiguration"
