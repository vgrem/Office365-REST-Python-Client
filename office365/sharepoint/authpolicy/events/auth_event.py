from office365.sharepoint.base_entity import BaseEntity


class SPAuthEvent(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.AuthPolicy.Events.SPAuthEvent"


