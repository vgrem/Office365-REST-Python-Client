from client.client_value_object import ClientValueObject


class WebCreationInformation(ClientValueObject):
    """Represents metadata about site creation."""

    def __init__(self):
        self.Title = None
        self.Url = None
        self.metadata_type = "SP.WebCreationInformation"

    def get_metadata(self):
        return {'parameters': ClientValueObject.get_metadata(self)}




