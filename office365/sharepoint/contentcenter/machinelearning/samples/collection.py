from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.contentcenter.machinelearning.samples.sample import SPMachineLearningSample


class SPMachineLearningSampleCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(SPMachineLearningSampleCollection, self).__init__(context, SPMachineLearningSample, resource_path)

    def get_by_title(self, title):
        """
        :param str title: The title of the model to return.
        """
        return SPMachineLearningSample(self.context,
                                       ServiceOperationPath("GetByTitle", [title], self.resource_path))
