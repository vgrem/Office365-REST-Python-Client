from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.authentication.methods.target import (
        AuthenticationMethodTarget,
    )
    from office365.directory.certificates.x509.authenticationmodeconfiguration import (
        X509CertificateAuthenticationModeConfiguration,
    )
    from office365.directory.certificates.x509.authority_scope import (
        X509CertificateAuthorityScope,
    )
    from office365.directory.certificates.x509.crlvalidationconfiguration import (
        X509CertificateCRLValidationConfiguration,
    )
    from office365.directory.certificates.x509.issuer_hints_configuration import (
        X509CertificateIssuerHintsConfiguration,
    )
    from office365.directory.certificates.x509.userbinding import (
        X509CertificateUserBinding,
    )


class X509CertificateAuthenticationMethodConfiguration(Entity):
    @property
    def authentication_mode_configuration(self) -> X509CertificateAuthenticationModeConfiguration:
        """Gets the authenticationModeConfiguration property"""
        from office365.directory.certificates.x509.authenticationmodeconfiguration import (
            X509CertificateAuthenticationModeConfiguration,
        )

        return self.properties.get("authenticationModeConfiguration", X509CertificateAuthenticationModeConfiguration())

    @property
    def certificate_authority_scopes(self) -> ClientValueCollection[X509CertificateAuthorityScope]:
        """Gets the certificateAuthorityScopes property"""
        from office365.directory.certificates.x509.authority_scope import (
            X509CertificateAuthorityScope,
        )

        return self.properties.get(
            "certificateAuthorityScopes",
            ClientValueCollection[X509CertificateAuthorityScope](X509CertificateAuthorityScope),
        )

    @property
    def certificate_user_bindings(self) -> ClientValueCollection[X509CertificateUserBinding]:
        """Gets the certificateUserBindings property"""
        from office365.directory.certificates.x509.userbinding import (
            X509CertificateUserBinding,
        )

        return self.properties.get(
            "certificateUserBindings", ClientValueCollection[X509CertificateUserBinding](X509CertificateUserBinding)
        )

    @property
    def crl_validation_configuration(self) -> X509CertificateCRLValidationConfiguration:
        """Gets the crlValidationConfiguration property"""
        from office365.directory.certificates.x509.crlvalidationconfiguration import (
            X509CertificateCRLValidationConfiguration,
        )

        return self.properties.get("crlValidationConfiguration", X509CertificateCRLValidationConfiguration())

    @property
    def issuer_hints_configuration(self) -> X509CertificateIssuerHintsConfiguration:
        """Gets the issuerHintsConfiguration property"""
        from office365.directory.certificates.x509.issuer_hints_configuration import (
            X509CertificateIssuerHintsConfiguration,
        )

        return self.properties.get("issuerHintsConfiguration", X509CertificateIssuerHintsConfiguration())

    @property
    def include_targets(self) -> EntityCollection[AuthenticationMethodTarget]:
        """Gets the includeTargets property"""
        from office365.directory.authentication.methods.target import (
            AuthenticationMethodTarget,
        )

        return self.properties.get(
            "includeTargets",
            EntityCollection[AuthenticationMethodTarget](
                self.context, AuthenticationMethodTarget, ResourcePath("includeTargets", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.X509CertificateAuthenticationMethodConfiguration"
