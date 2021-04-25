from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.taxonomy.term_set import TermSet


class TermSetCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(TermSetCollection, self).__init__(context, TermSet, resource_path)
