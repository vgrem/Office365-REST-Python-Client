from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.objects.object import DirectoryObject
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.certificates.authority_detail import (
        CertificateAuthorityDetail,
    )


class CertificateBasedAuthPki(DirectoryObject):
    """The collection of public key infrastructure (PKI) instances for the certificate-based authentication method.
    The certificate-based authentication method must be enabled in the tenant for you to manage these PKI instances.
    """

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def status(self) -> Optional[str]:
        """Gets the status property"""
        return self.properties.get("status", None)

    @property
    def status_details(self) -> Optional[str]:
        """Gets the statusDetails property"""
        return self.properties.get("statusDetails", None)

    @property
    def certificate_authorities(self) -> EntityCollection[CertificateAuthorityDetail]:
        """Gets the certificateAuthorities property"""
        from office365.directory.certificates.authority_detail import (
            CertificateAuthorityDetail,
        )

        return self.properties.get(
            "certificateAuthorities",
            EntityCollection[CertificateAuthorityDetail](
                self.context, CertificateAuthorityDetail, ResourcePath("certificateAuthorities", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CertificateBasedAuthPki"
