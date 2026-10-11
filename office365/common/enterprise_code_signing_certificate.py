from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.certificates.status import CertificateStatus


class EnterpriseCodeSigningCertificate(Entity):
    @property
    def content(self) -> Optional[bytes]:
        """Gets the content property"""
        return self.properties.get("content", None)

    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def issuer(self) -> Optional[str]:
        """Gets the issuer property"""
        return self.properties.get("issuer", None)

    @property
    def issuer_name(self) -> Optional[str]:
        """Gets the issuerName property"""
        return self.properties.get("issuerName", None)

    @property
    def status(self) -> CertificateStatus:
        """Gets the status property"""
        from office365.directory.certificates.status import CertificateStatus

        return self.properties.get("status", CertificateStatus.notProvisioned)

    @property
    def subject(self) -> Optional[str]:
        """Gets the subject property"""
        return self.properties.get("subject", None)

    @property
    def subject_name(self) -> Optional[str]:
        """Gets the subjectName property"""
        return self.properties.get("subjectName", None)

    @property
    def upload_date_time(self) -> Optional[datetime]:
        """Gets the uploadDateTime property"""
        return self.properties.get("uploadDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EnterpriseCodeSigningCertificate"
