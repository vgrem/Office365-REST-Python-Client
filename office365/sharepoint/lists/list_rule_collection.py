from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.lists.list_rule import SPListRule


class SPListRuleCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(SPListRuleCollection, self).__init__(context, SPListRule, resource_path)
