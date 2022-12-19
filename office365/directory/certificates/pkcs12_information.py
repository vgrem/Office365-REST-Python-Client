from office365.runtime.client_value import ClientValue


class Pkcs12CertificateInformation(ClientValue):
    """Represents the public information of a Pkcs12 certificate."""

    def __init__(self, thumbprint=None, is_active=None):
        """
        :param str thumbprint: The certificate thumbprint

        """
        self.thumbprint = thumbprint
        self.isActive = is_active
