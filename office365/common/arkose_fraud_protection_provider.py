from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class ArkoseFraudProtectionProvider(Entity):
    @property
    def client_sub_domain(self) -> Optional[str]:
        """Gets the clientSubDomain property"""
        return self.properties.get("clientSubDomain", None)

    @property
    def private_key(self) -> Optional[str]:
        """Gets the privateKey property"""
        return self.properties.get("privateKey", None)

    @property
    def public_key(self) -> Optional[str]:
        """Gets the publicKey property"""
        return self.properties.get("publicKey", None)

    @property
    def verify_sub_domain(self) -> Optional[str]:
        """Gets the verifySubDomain property"""
        return self.properties.get("verifySubDomain", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ArkoseFraudProtectionProvider"
