from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.passkey_authentication_method_target import (
        PasskeyAuthenticationMethodTarget,
    )
    from office365.common.passkey_profile import PasskeyProfile
    from office365.directory.authentication.fido2keyrestrictions import (
        Fido2KeyRestrictions,
    )


class Fido2AuthenticationMethodConfiguration(Entity):
    @property
    def default_passkey_profile(self) -> Optional[str]:
        """Gets the defaultPasskeyProfile property"""
        return self.properties.get("defaultPasskeyProfile", None)

    @property
    def is_attestation_enforced(self) -> Optional[bool]:
        """Gets the isAttestationEnforced property"""
        return self.properties.get("isAttestationEnforced", None)

    @property
    def is_self_service_registration_allowed(self) -> Optional[bool]:
        """Gets the isSelfServiceRegistrationAllowed property"""
        return self.properties.get("isSelfServiceRegistrationAllowed", None)

    @property
    def key_restrictions(self) -> Fido2KeyRestrictions:
        """Gets the keyRestrictions property"""
        from office365.directory.authentication.fido2keyrestrictions import (
            Fido2KeyRestrictions,
        )

        return self.properties.get("keyRestrictions", Fido2KeyRestrictions())

    @property
    def include_targets(self) -> EntityCollection[PasskeyAuthenticationMethodTarget]:
        """Gets the includeTargets property"""
        from office365.common.passkey_authentication_method_target import (
            PasskeyAuthenticationMethodTarget,
        )

        return self.properties.get(
            "includeTargets",
            EntityCollection[PasskeyAuthenticationMethodTarget](
                self.context, PasskeyAuthenticationMethodTarget, ResourcePath("includeTargets", self.resource_path)
            ),
        )

    @property
    def passkey_profiles(self) -> EntityCollection[PasskeyProfile]:
        """Gets the passkeyProfiles property"""
        from office365.common.passkey_profile import PasskeyProfile

        return self.properties.get(
            "passkeyProfiles",
            EntityCollection[PasskeyProfile](
                self.context, PasskeyProfile, ResourcePath("passkeyProfiles", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Fido2AuthenticationMethodConfiguration"
