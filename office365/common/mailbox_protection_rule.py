from __future__ import annotations

from typing import Optional

from office365.directory.protection.rules.base import ProtectionRuleBase


class MailboxProtectionRule(ProtectionRuleBase):
    @property
    def mailbox_expression(self) -> Optional[str]:
        """Gets the mailboxExpression property"""
        return self.properties.get("mailboxExpression", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MailboxProtectionRule"
