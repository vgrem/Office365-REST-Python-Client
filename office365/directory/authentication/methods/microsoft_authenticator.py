from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.authentication.methods.method import AuthenticationMethod
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.device import Device


class MicrosoftAuthenticatorAuthenticationMethod(AuthenticationMethod):
    """A representation of the Microsoft Authenticator app registered to a user. Microsoft Authenticator
    is an authentication method."""

    @property
    def device_tag(self) -> Optional[str]:
        """Gets the deviceTag property"""
        return self.properties.get("deviceTag", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def phone_app_version(self) -> Optional[str]:
        """Gets the phoneAppVersion property"""
        return self.properties.get("phoneAppVersion", None)

    @property
    def device(self) -> Device:
        """Gets the device property"""
        from office365.intune.devices.device import Device

        return self.properties.get("device", Device(self.context, ResourcePath("device", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MicrosoftAuthenticatorAuthenticationMethod"
