import math
import time

from office365.runtime.client_value import ClientValue


class ContextWebInformation(ClientValue):
    """Specifies metadata about a site."""

    def __init__(self, form_digest_value=None, form_digest_timeout_secs=None):
        """
        :param str form_digest_value: Specifies a valid form digest for the site
        :param int form_digest_timeout_secs: Specifies the amount of time in seconds before security validation expires.
        """
        super(ContextWebInformation, self).__init__()
        self.FormDigestValue = form_digest_value
        self.FormDigestTimeoutSeconds = form_digest_timeout_secs
        self.LibraryVersion = None
        self.SiteFullUrl = None
        self.SupportedSchemaVersions = None
        self.WebFullUrl = None
        self._valid_from = time.time()

    def reset(self):
        pass

    @property
    def is_valid(self):
        """
        Determines whether FormDigest has been expired or not
        """
        if self.FormDigestTimeoutSeconds is None:
            return False

        expires_in_sec = math.ceil(time.time() - self._valid_from)
        return expires_in_sec < self.FormDigestTimeoutSeconds
