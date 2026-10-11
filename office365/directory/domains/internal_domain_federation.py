from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.signing_certificate_update_status import (
        SigningCertificateUpdateStatus,
    )
    from office365.directory.domains.federatedidpmfabehavior import (
        FederatedIdpMfaBehavior,
    )
    from office365.directory.domains.promptloginbehavior import PromptLoginBehavior
    from office365.intune.devices.management.system_browser_enabled_on import SystemBrowserEnabledOn


class InternalDomainFederation(Entity):
    @property
    def active_sign_in_uri(self) -> Optional[str]:
        """Gets the activeSignInUri property"""
        return self.properties.get("activeSignInUri", None)

    @property
    def federated_idp_mfa_behavior(self) -> FederatedIdpMfaBehavior:
        """Gets the federatedIdpMfaBehavior property"""
        from office365.directory.domains.federatedidpmfabehavior import (
            FederatedIdpMfaBehavior,
        )

        return self.properties.get("federatedIdpMfaBehavior", FederatedIdpMfaBehavior.acceptIfMfaDoneByFederatedIdp)

    @property
    def is_signed_authentication_request_required(self) -> Optional[bool]:
        """Gets the isSignedAuthenticationRequestRequired property"""
        return self.properties.get("isSignedAuthenticationRequestRequired", None)

    @property
    def next_signing_certificate(self) -> Optional[str]:
        """Gets the nextSigningCertificate property"""
        return self.properties.get("nextSigningCertificate", None)

    @property
    def password_reset_uri(self) -> Optional[str]:
        """Gets the passwordResetUri property"""
        return self.properties.get("passwordResetUri", None)

    @property
    def prompt_login_behavior(self) -> PromptLoginBehavior:
        """Gets the promptLoginBehavior property"""
        from office365.directory.domains.promptloginbehavior import PromptLoginBehavior

        return self.properties.get("promptLoginBehavior", PromptLoginBehavior.translateToFreshPasswordAuthentication)

    @property
    def signing_certificate_update_status(self) -> SigningCertificateUpdateStatus:
        """Gets the signingCertificateUpdateStatus property"""
        from office365.directory.authentication.signing_certificate_update_status import (
            SigningCertificateUpdateStatus,
        )

        return self.properties.get("signingCertificateUpdateStatus", SigningCertificateUpdateStatus())

    @property
    def sign_out_uri(self) -> Optional[str]:
        """Gets the signOutUri property"""
        return self.properties.get("signOutUri", None)

    @property
    def system_browser_enabled_on(self) -> SystemBrowserEnabledOn:
        """Gets the systemBrowserEnabledOn property"""
        from office365.intune.devices.management.system_browser_enabled_on import SystemBrowserEnabledOn

        return self.properties.get("systemBrowserEnabledOn", SystemBrowserEnabledOn.none)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InternalDomainFederation"
