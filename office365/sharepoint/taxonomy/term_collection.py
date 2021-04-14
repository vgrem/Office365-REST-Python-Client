from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.taxonomy.term import Term


class TermCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(TermCollection, self).__init__(context, Term, resource_path)
