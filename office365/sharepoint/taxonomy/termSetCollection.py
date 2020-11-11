from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.taxonomy.term_set import TermSet


class TermSetCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(TermSetCollection, self).__init__(context, TermSet, resource_path)
