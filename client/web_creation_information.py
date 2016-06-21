from client.client_value_object import ClientValueObject


class WebCreationInformation(ClientValueObject):
    """Represents metadata about site creation."""

    def __init__(self):
        super(WebCreationInformation, self).__init__()
        self.Title = None
        self.Url = None
        self.metadata_type = "SP.WebCreationInformation"

    def metadata(self):
        return {'parameters': super(WebCreationInformation, self).metadata}
