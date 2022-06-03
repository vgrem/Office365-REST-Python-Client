from office365.runtime.client_value import ClientValue


class SiteScriptMetadata(ClientValue):

    def __init__(self, _id=None, content=None, description=None):
        """
        :param str content:
        :param str description:
        """
        self.Id = _id
        self.Content = content
        self.Description = description
