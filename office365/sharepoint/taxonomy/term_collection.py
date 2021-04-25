from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.taxonomy.term import Term


class TermCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(TermCollection, self).__init__(context, Term, resource_path)
