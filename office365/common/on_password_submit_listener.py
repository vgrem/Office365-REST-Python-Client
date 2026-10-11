from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identities.on_password_submit_handler import (
        OnPasswordSubmitHandler,
    )


class OnPasswordSubmitListener(Entity):
    @property
    def handler(self) -> OnPasswordSubmitHandler:
        """Gets the handler property"""
        from office365.directory.identities.on_password_submit_handler import (
            OnPasswordSubmitHandler,
        )

        return self.properties.get("handler", OnPasswordSubmitHandler())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnPasswordSubmitListener"
