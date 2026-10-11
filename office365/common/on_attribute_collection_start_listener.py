from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.attributecollection.start_handler import (
        OnAttributeCollectionStartHandler,
    )


class OnAttributeCollectionStartListener(Entity):
    @property
    def handler(self) -> OnAttributeCollectionStartHandler:
        """Gets the handler property"""
        from office365.directory.authentication.attributecollection.start_handler import (
            OnAttributeCollectionStartHandler,
        )

        return self.properties.get("handler", OnAttributeCollectionStartHandler())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnAttributeCollectionStartListener"
