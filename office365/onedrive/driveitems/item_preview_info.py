from office365.runtime.client_value import ClientValue


class ItemPreviewInfo(ClientValue):
    """Contains information about how to embed a preview of a driveItem."""

    def __init__(self, post_url=None):
        self.postUrl = post_url

