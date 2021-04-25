from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.lists.list_rule import SPListRule


class SPListRuleCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(SPListRuleCollection, self).__init__(context, SPListRule, resource_path)
