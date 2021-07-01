from office365.runtime.client_value import ClientValue


class WikiPageCreationInformation(ClientValue):

    def __init__(self, server_relative_url, content):
        """

        :param str server_relative_url:
        :param str content:
        """
        super(WikiPageCreationInformation, self).__init__()
        self.ServerRelativeUrl = server_relative_url
        self.WikiHtmlContent = content

    @property
    def entity_type_name(self):
        return "SP.Utilities.WikiPageCreationInformation"
