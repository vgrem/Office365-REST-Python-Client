from office365.runtime.client_value import ClientValue


class WikiPageCreationInformation(ClientValue):

    def __init__(self, server_relative_url, content):
        super().__init__()
        self.ServerRelativeUrl = server_relative_url
        self.WikiHtmlContent = content
