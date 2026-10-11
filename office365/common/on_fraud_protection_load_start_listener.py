from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.identities.providers.on_fraud_protection_load_start_handler import (
        OnFraudProtectionLoadStartHandler,
    )


class OnFraudProtectionLoadStartListener(Entity):
    @property
    def handler(self) -> OnFraudProtectionLoadStartHandler:
        """Gets the handler property"""
        from office365.directory.identities.providers.on_fraud_protection_load_start_handler import (
            OnFraudProtectionLoadStartHandler,
        )

        return self.properties.get("handler", OnFraudProtectionLoadStartHandler())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnFraudProtectionLoadStartListener"
