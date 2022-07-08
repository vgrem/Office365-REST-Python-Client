from office365.runtime.client_value import ClientValue


class CommentInformation(ClientValue):

    def __init__(self, text=None, mentions=None):
        self.text = text
        self.mentions = mentions
