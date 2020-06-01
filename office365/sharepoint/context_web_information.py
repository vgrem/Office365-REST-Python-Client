from office365.runtime.client_value_object import ClientValueObject


class ContextWebInformation(ClientValueObject):
    """The context information for a site."""

    def __init__(self):
        super(ContextWebInformation, self).__init__()
        self.FormDigestValue = None
        self.FormDigestTimeoutSeconds = None
        self.LibraryVersion = None
        self.SiteFullUrl = None
        self.SupportedSchemaVersions = None
        self.WebFullUrl = None
