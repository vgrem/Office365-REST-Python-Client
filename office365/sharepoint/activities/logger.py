from office365.sharepoint.base_entity import BaseEntity


class ActivityLogger(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Internal.ActivityLogger"
