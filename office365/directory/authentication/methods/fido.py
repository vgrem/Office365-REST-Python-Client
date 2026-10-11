from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.authentication.methods.method import AuthenticationMethod
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.authentication.methods.attestationlevel import (
        AttestationLevel,
    )
    from office365.directory.authentication.methods.passkey_type import PasskeyType
    from office365.directory.authentication.webauthn_public_key_credential import (
        WebauthnPublicKeyCredential,
    )


class Fido2AuthenticationMethod(AuthenticationMethod):
    """Representation of a FIDO2 security key registered to a user. FIDO2 is a sign-in authentication method."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def attestation_certificates(self) -> StringCollection:
        """The attestation certificate(s) attached to this security key."""
        return self.properties.get("attestationCertificates", StringCollection())

    @property
    def created_datetime(self) -> datetime:
        """The timestamp when this key was registered to the user."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """The display name of the key as given by the user."""
        return self.properties.get("displayName", None)

    @property
    def model(self) -> Optional[str]:
        """The manufacturer-assigned model of the FIDO2 security key."""
        return self.properties.get("model", None)

    @property
    def aa_guid(self) -> Optional[str]:
        """Gets the aaGuid property"""
        return self.properties.get("aaGuid", None)

    @property
    def attestation_level(self) -> AttestationLevel:
        """Gets the attestationLevel property"""
        from office365.directory.authentication.methods.attestationlevel import (
            AttestationLevel,
        )

        return self.properties.get("attestationLevel", AttestationLevel.attested)

    @property
    def passkey_type(self) -> PasskeyType:
        """Gets the passkeyType property"""
        from office365.directory.authentication.methods.passkey_type import PasskeyType

        return self.properties.get("passkeyType", PasskeyType.deviceBound)

    @property
    def public_key_credential(self) -> WebauthnPublicKeyCredential:
        """Gets the publicKeyCredential property"""
        from office365.directory.authentication.webauthn_public_key_credential import (
            WebauthnPublicKeyCredential,
        )

        return self.properties.get("publicKeyCredential", WebauthnPublicKeyCredential())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Fido2AuthenticationMethod"
