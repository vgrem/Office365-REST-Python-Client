from office365.sharepoint.base_entity import BaseEntity


class HostedAppsManager(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.ClientSideComponent.HostedAppsManager"
