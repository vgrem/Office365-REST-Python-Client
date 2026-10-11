from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.security.account import Account


class IdentityAccounts(Entity):
    @property
    def cloud_security_identifier(self) -> Optional[str]:
        """Gets the cloudSecurityIdentifier property"""
        return self.properties.get("cloudSecurityIdentifier", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def domain(self) -> Optional[str]:
        """Gets the domain property"""
        return self.properties.get("domain", None)

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def on_premises_security_identifier(self) -> Optional[str]:
        """Gets the onPremisesSecurityIdentifier property"""
        return self.properties.get("onPremisesSecurityIdentifier", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IdentityAccounts"

    @property
    def accounts(self) -> ClientValueCollection[Account]:
        """Gets the accounts property"""
        from office365.security.account import Account

        return self.properties.get("accounts", ClientValueCollection[Account](Account))
