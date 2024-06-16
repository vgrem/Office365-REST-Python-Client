from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


class ResourceAction(ClientValue):
    """ """

    def __init__(self):
        self.allowedResourceActions = StringCollection()
        self.notAllowedResourceActions = StringCollection()
