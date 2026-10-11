from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identities.on_user_create_start_handler import (
        OnUserCreateStartHandler,
    )


class OnUserCreateStartListener(Entity):
    @property
    def handler(self) -> OnUserCreateStartHandler:
        """Gets the handler property"""
        from office365.directory.identities.on_user_create_start_handler import (
            OnUserCreateStartHandler,
        )

        return self.properties.get("handler", OnUserCreateStartHandler())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnUserCreateStartListener"
