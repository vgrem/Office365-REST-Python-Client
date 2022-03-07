from office365.runtime.client_value import ClientValue


class CertificateAuthority(ClientValue):
    """Represents a certificate authority."""

    def __init__(self, certificate=None):
        """
        :param str certificate: The base64 encoded string representing the public certificate.
        """
        super(CertificateAuthority, self).__init__()
        self.certificate = certificate
