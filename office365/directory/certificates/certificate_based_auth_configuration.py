from office365.directory.certificates.certificate_authority import CertificateAuthority
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection


class CertificateBasedAuthConfiguration(Entity):

    @property
    def certificate_authorities(self):
        return self.properties.get("certificateAuthorities", ClientValueCollection(CertificateAuthority))
