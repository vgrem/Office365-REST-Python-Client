from office365.sharepoint.base_entity import BaseEntity


class SPMachineLearningSample(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningSample"


