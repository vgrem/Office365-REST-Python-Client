from office365.runtime.client_value import ClientValue


class FieldUrlValue(ClientValue):

    def __init__(self, Url=None, Description=None):
        super(FieldUrlValue, self).__init__()
        self.Url = Url
        self.Description = Description

    @property
    def entity_type_name(self):
        return "SP.FieldUrlValue"
