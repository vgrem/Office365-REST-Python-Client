from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.authentication.methods.keystrength import (
        AuthenticationMethodKeyStrength,
    )
    from office365.directory.authentication.methods.platform import (
        AuthenticationMethodPlatform,
    )
    from office365.intune.devices.device import Device


class PlatformCredentialAuthenticationMethod(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def key_strength(self) -> AuthenticationMethodKeyStrength:
        """Gets the keyStrength property"""
        from office365.directory.authentication.methods.keystrength import (
            AuthenticationMethodKeyStrength,
        )

        return self.properties.get("keyStrength", AuthenticationMethodKeyStrength.normal)

    @property
    def platform(self) -> AuthenticationMethodPlatform:
        """Gets the platform property"""
        from office365.directory.authentication.methods.platform import (
            AuthenticationMethodPlatform,
        )

        return self.properties.get("platform", AuthenticationMethodPlatform.unknown)

    @property
    def device(self) -> Device:
        """Gets the device property"""
        from office365.intune.devices.device import Device

        return self.properties.get("device", Device(self.context, ResourcePath("device", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PlatformCredentialAuthenticationMethod"
