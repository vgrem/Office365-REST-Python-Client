from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.taxonomy.term_group import TermGroup


class TermGroupCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(TermGroupCollection, self).__init__(context, TermGroup, resource_path)
