from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class MailboxProtectionRule(Entity):
    @property
    def mailbox_expression(self) -> Optional[str]:
        """Gets the mailboxExpression property"""
        return self.properties.get("mailboxExpression", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MailboxProtectionRule"
