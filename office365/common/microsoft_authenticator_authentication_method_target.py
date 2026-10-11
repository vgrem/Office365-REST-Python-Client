from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.microsoftauthenticatorauthenticationmode import (
        MicrosoftAuthenticatorAuthenticationMode,
    )


class MicrosoftAuthenticatorAuthenticationMethodTarget(Entity):
    @property
    def authentication_mode(self) -> MicrosoftAuthenticatorAuthenticationMode:
        """Gets the authenticationMode property"""
        from office365.directory.authentication.microsoftauthenticatorauthenticationmode import (
            MicrosoftAuthenticatorAuthenticationMode,
        )

        return self.properties.get("authenticationMode", MicrosoftAuthenticatorAuthenticationMode.deviceBasedPush)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MicrosoftAuthenticatorAuthenticationMethodTarget"
