from office365.sharepoint.base_entity import BaseEntity


class MountService(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.AddToOneDrive.MountService"
