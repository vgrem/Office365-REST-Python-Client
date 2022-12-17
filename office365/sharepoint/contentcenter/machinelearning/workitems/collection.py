from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.contentcenter.machinelearning.workitems.item import SPMachineLearningWorkItem


class SPMachineLearningWorkItemCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(SPMachineLearningWorkItemCollection, self).__init__(context, SPMachineLearningWorkItem, resource_path)
