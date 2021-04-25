from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.taxonomy.term_group import TermGroup


class TermGroupCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(TermGroupCollection, self).__init__(context, TermGroup, resource_path)
