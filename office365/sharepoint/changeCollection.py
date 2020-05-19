from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.change import Change


class ChangeCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(ChangeCollection, self).__init__(context, Change, resource_path)
