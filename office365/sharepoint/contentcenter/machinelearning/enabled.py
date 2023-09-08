from office365.sharepoint.base_entity import BaseEntity


class SPMachineLearningEnabled(BaseEntity):

    @property
    def is_syntex_payg_enabled(self):
        """
        :rtype: bool or None
        """
        return self.properties.get("IsSyntexPAYGEnabled", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningEnabled"
