from office365.runtime.client_value import ClientValue


class KeyCredential(ClientValue):
    """
    Contains a key credential associated with an application .
    The keyCredentials property of the application entity is a collection of keyCredential.
    """

    def __init__(self, custom_key_identifier=None, display_name=None, end_datetime=None):
        """
        :param str custom_key_identifier: A 40-character binary type that can be used to identify the credential.
           Optional. When not provided in the payload, defaults to the thumbprint of the certificate.
        :param str display_name: Friendly name for the key. Optional.
        :param datetime end_datetime: The date and time at which the credential expires. The DateTimeOffset type
            represents date and time information using ISO 8601 format and is always in UTC time.
            For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.
        """
        self.customKeyIdentifier = custom_key_identifier
        self.displayName = display_name
        self.endDateTime = end_datetime
