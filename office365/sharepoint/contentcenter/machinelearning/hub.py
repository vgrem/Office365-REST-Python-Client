from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.contentcenter.machinelearning.model_collection import SPMachineLearningModelCollection


class SPMachineLearningHub(BaseEntity):

    def get_models(self, list_id=None, model_types=None, publication_types=None,
                   include_management_not_allowed_models=None):
        """
        :param str list_id:
        :param int model_types:
        :param int publication_types:
        :param bool include_management_not_allowed_models:
        """
        return_type = SPMachineLearningModelCollection(self.context)
        payload = {
            "listId": list_id,
            "modelTypes": model_types,
            "publicationTypes": publication_types,
            "includeManagementNotAllowedModels": include_management_not_allowed_models
        }
        qry = ServiceOperationQuery(self, "GetModels", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def is_default_content_center(self):
        """
        :rtype: bool
        """
        return self.properties.get("IsDefaultContentCenter", None)

    @property
    def machine_learning_capture_enabled(self):
        """
        :rtype: bool
        """
        return self.properties.get("MachineLearningCaptureEnabled", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningHub"
