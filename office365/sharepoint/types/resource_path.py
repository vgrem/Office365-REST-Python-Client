from office365.runtime.client_value import ClientValue


class ResourcePath(ClientValue):

    def __init__(self, decoded_url=None):
        """
        Represents the full (absolute) or parts (relative) path of a site collection, web, file, folder or
        other artifacts in the database.

        :param str decoded_url: Gets the path in the decoded form.
        """
        super(ResourcePath, self).__init__()
        self.DecodedUrl = decoded_url

    @property
    def entity_type_name(self):
        return "SP.ResourcePath"

    def __str__(self):
        return str(self.DecodedUrl)
