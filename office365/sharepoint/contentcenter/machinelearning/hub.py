from office365.sharepoint.base_entity import BaseEntity


class SPMachineLearningHub(BaseEntity):

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
