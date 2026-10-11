from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.applications.attestation_enforcement import (
        AttestationEnforcement,
    )
    from office365.directory.applications.passkey_types import PasskeyTypes
    from office365.directory.authentication.fido2keyrestrictions import (
        Fido2KeyRestrictions,
    )


class PasskeyProfile(Entity):
    @property
    def attestation_enforcement(self) -> AttestationEnforcement:
        """Gets the attestationEnforcement property"""
        from office365.directory.applications.attestation_enforcement import (
            AttestationEnforcement,
        )

        return self.properties.get("attestationEnforcement", AttestationEnforcement.disabled)

    @property
    def key_restrictions(self) -> Fido2KeyRestrictions:
        """Gets the keyRestrictions property"""
        from office365.directory.authentication.fido2keyrestrictions import (
            Fido2KeyRestrictions,
        )

        return self.properties.get("keyRestrictions", Fido2KeyRestrictions())

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def passkey_types(self) -> PasskeyTypes:
        """Gets the passkeyTypes property"""
        from office365.directory.applications.passkey_types import PasskeyTypes

        return self.properties.get("passkeyTypes", PasskeyTypes.deviceBound)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PasskeyProfile"
