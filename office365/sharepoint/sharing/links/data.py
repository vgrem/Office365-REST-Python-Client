from office365.runtime.client_value import ClientValue


class SharingLinkData(ClientValue):
    """
    This class stores basic overview information about the link URL, including limited data
    about the object the link URL refers to and any additional sharing link data if the link URL
    is a tokenized sharing link.
    """

    def __init__(self, blocks_download=None, description=None):
        """
        :param bool blocks_download:
        :param str description:
        """
        self.BlocksDownload = blocks_download
        self.Description = description
