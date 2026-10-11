from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class ExchangeSettings(Entity):
    @property
    def primary_mailbox_id(self) -> Optional[str]:
        """Gets the primaryMailboxId property"""
        return self.properties.get("primaryMailboxId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ExchangeSettings"
