class ContextWebInformation(object):
    """The context information for a site."""

    def __init__(self):
        self._webFullUrl = None
        self._supportedSchemaVersions = None
        self._siteFullUrl = None
        self._libraryVersion = None
        self._formDigestValue = None
        self._formDigestTimeoutSeconds = None

    def from_json(self, properties):
        self._webFullUrl = properties['WebFullUrl']
        self._supportedSchemaVersions = properties['SupportedSchemaVersions']
        self._siteFullUrl = properties['SiteFullUrl']
        self._libraryVersion = properties['LibraryVersion']
        self._formDigestValue = properties['FormDigestValue']
        self._formDigestTimeoutSeconds = properties['FormDigestTimeoutSeconds']

    @property
    def form_digest_timeout_seconds(self):
        """The amount of time in seconds that the form digest will timeout."""
        return self._formDigestTimeoutSeconds

    @property
    def form_digest_value(self):
        """The form digest value."""
        return self._formDigestValue

    @property
    def library_version(self):
        """The library version."""
        return self._libraryVersion

    @property
    def site_full_url(self):
        """The full URL of the site collection context."""
        return self._siteFullUrl

    @property
    def supported_schema_versions(self):
        """The supported client-side object model request schema version."""
        return self._supportedSchemaVersions

    @property
    def web_full_url(self):
        """The full URL of the site context."""
        return self._webFullUrl
