from office365.runtime.client_value import ClientValue


class PageLinks(ClientValue):
    """Links for opening a OneNote page."""

    def __init__(self, onenote_client_url=None, onenote_web_url=None):
        """
        :param str onenote_client_url: Opens the page in the OneNote native client if it's installed.
        :param str onenote_web_url: Opens the page in OneNote on the web.
        """
        super(PageLinks, self).__init__()
        self.oneNoteClientUrl = onenote_client_url
        self.oneNoteWebUrl = onenote_web_url
