from office365.runtime.client_value import ClientValue


class ResourcePath(ClientValue):

    def __init__(self, decoded_url=None):
        super(ResourcePath, self).__init__()
        self.DecodedUrl = decoded_url

    @property
    def entity_type_name(self):
        return "SP.ResourcePath"

    def __str__(self):
        return "DecodedUrl='{0}'".format(self.DecodedUrl)
