from office365.runtime.client_value import ClientValue


class PublicationFacet(ClientValue):

    def __init__(self, level=None, versionId=None):
        """

        :param str level: The state of publication for this document. Either published or checkout. Read-only.
        :param str versionId: The unique identifier for the version that is visible to the current caller. Read-only.
        """
        super(PublicationFacet, self).__init__()
        self.level = level
        self.versionId = versionId
