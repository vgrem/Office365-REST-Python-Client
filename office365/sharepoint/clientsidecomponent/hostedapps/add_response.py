from office365.sharepoint.base_entity import BaseEntity


class HostedAppAddResponse(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.ClientSideComponent.HostedAppAddResponse"
