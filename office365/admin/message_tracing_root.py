from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.admin.exchange.exchange_message_trace import ExchangeMessageTrace


class MessageTracingRoot(Entity):
    @property
    def message_traces(self) -> EntityCollection[ExchangeMessageTrace]:
        """Gets the messageTraces property"""
        from office365.admin.exchange.exchange_message_trace import ExchangeMessageTrace

        return self.properties.get(
            "messageTraces",
            EntityCollection[ExchangeMessageTrace](
                self.context, ExchangeMessageTrace, ResourcePath("messageTraces", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MessageTracingRoot"
