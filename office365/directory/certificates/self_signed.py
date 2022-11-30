from office365.runtime.client_value import ClientValue


class SelfSignedCertificate(ClientValue):
    """Contains the public part of a signing certificate."""

    def __init__(self, display_name=None):
        """
        :param str display_name:
        """
        self.displayName = display_name

