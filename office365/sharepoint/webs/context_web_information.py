from office365.runtime.client_value import ClientValue


class ContextWebInformation(ClientValue):
    """The context information for a site."""

    def __init__(self):
        super(ContextWebInformation, self).__init__()
        self.FormDigestValue = None
        self.FormDigestTimeoutSeconds = None
        self.LibraryVersion = None
        self.SiteFullUrl = None
        self.SupportedSchemaVersions = None
        self.WebFullUrl = None
