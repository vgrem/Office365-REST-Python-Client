from __future__ import annotations

from office365.entity import Entity
from office365.runtime.types.collections import GuidCollection


class PasskeyAuthenticationMethodTarget(Entity):
    @property
    def allowed_passkey_profiles(self) -> GuidCollection:
        """Gets the allowedPasskeyProfiles property"""
        return self.properties.get("allowedPasskeyProfiles", GuidCollection())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PasskeyAuthenticationMethodTarget"
