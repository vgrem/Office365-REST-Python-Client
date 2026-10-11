from __future__ import annotations

from enum import Enum


class Action(Enum):
    disable = "1"
    enable = "2"
    forcePasswordReset = "3"
    revokeAllSessions = "4"
    requireUserToSignInAgain = "5"
    markUserAsCompromised = "6"
    unknownFutureValue = "7"

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Action"
