from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.sharepoint.permissions.base_permissions import BasePermissions


@dataclass
class RoleDefinitionCreationInformation(ClientValue):
    BasePermissions: BasePermissions = field(default_factory=BasePermissions)
    Description: str | None = None
    Name: str | None = None
    Order: int | None = None
