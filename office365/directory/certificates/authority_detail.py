from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.certificates.authoritytype import CertificateAuthorityType


class CertificateAuthorityDetail(Entity):
    @property
    def certificate(self) -> Optional[bytes]:
        """Gets the certificate property"""
        return self.properties.get("certificate", None)

    @property
    def certificate_authority_type(self) -> CertificateAuthorityType:
        """Gets the certificateAuthorityType property"""
        from office365.directory.certificates.authoritytype import (
            CertificateAuthorityType,
        )

        return self.properties.get("certificateAuthorityType", CertificateAuthorityType.root)

    @property
    def certificate_revocation_list_url(self) -> Optional[str]:
        """Gets the certificateRevocationListUrl property"""
        return self.properties.get("certificateRevocationListUrl", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def delta_certificate_revocation_list_url(self) -> Optional[str]:
        """Gets the deltaCertificateRevocationListUrl property"""
        return self.properties.get("deltaCertificateRevocationListUrl", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def is_issuer_hint_enabled(self) -> Optional[bool]:
        """Gets the isIssuerHintEnabled property"""
        return self.properties.get("isIssuerHintEnabled", None)

    @property
    def issuer(self) -> Optional[str]:
        """Gets the issuer property"""
        return self.properties.get("issuer", None)

    @property
    def issuer_subject_key_identifier(self) -> Optional[str]:
        """Gets the issuerSubjectKeyIdentifier property"""
        return self.properties.get("issuerSubjectKeyIdentifier", None)

    @property
    def thumbprint(self) -> Optional[str]:
        """Gets the thumbprint property"""
        return self.properties.get("thumbprint", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CertificateAuthorityDetail"
