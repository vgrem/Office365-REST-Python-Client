from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identities.on_token_issuance_start_handler import (
        OnTokenIssuanceStartHandler,
    )


class OnTokenIssuanceStartListener(Entity):
    @property
    def handler(self) -> OnTokenIssuanceStartHandler:
        """Gets the handler property"""
        from office365.directory.identities.on_token_issuance_start_handler import (
            OnTokenIssuanceStartHandler,
        )

        return self.properties.get("handler", OnTokenIssuanceStartHandler())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnTokenIssuanceStartListener"
