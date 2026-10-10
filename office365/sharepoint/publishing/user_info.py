from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from office365.runtime.client_value import ClientValue


@dataclass
class UserInfo(ClientValue):
    """Represents user information of a user with consistent color and acronym for client rendering."""

    email: Optional[str] = None
    loginName: Optional[str] = None
    name: Optional[str] = None
    userPrincipalName: Optional[str] = None

    @property
    def entity_type_name(self):
        return "SP.Publishing.UserInfo"

    AccountName: str | None = None

    Acronym: str | None = None

    Color: str | None = None
