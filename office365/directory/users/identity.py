from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class UserIdentity(ClientValue):
    """
    In the context of an Azure AD audit log, this represents the user information that initiated or
    was affected by an audit activity.
    """

    displayName: str | None = None
    ipAddress: str | None = None
    userPrincipalName: str | None = None

    def __str__(self) -> str:
        """Best-effort human-readable label (name, UPN or IP)."""
        return self.displayName or self.userPrincipalName or self.ipAddress or ""

    @property
    def entity_type_name(self):
        return "microsoft.graph.UserIdentity"
