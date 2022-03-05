from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class CustomActionElement(ClientValue):
    """A class specifies a custom action element."""
    pass


class CustomActionElementCollection(ClientValue):

    def __init__(self):
        super(CustomActionElementCollection, self).__init__()
        self.Items = ClientValueCollection(CustomActionElement)



