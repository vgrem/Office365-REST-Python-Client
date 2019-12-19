from office365.runtime.client_value_object import ClientValueObject


class UploadSession(ClientValueObject):
    """The UploadSession resource provides information about how to upload large files to OneDrive, OneDrive for
    Business, or SharePoint document libraries. """

    def __init__(self):
        self.expirationDateTime = None
        self.nextExpectedRanges = None
        self.uploadUrl = None
