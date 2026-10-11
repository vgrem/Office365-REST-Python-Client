from __future__ import annotations

from enum import Enum


class MailboxConfigurationType(Enum):
    mailForwardingRule = "0"
    owaSettings = "1"
    ewsSettings = "2"
    mailDelegation = "3"
    userInboxRule = "4"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.MailboxConfigurationType"
