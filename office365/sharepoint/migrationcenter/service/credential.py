from office365.sharepoint.base_entity import BaseEntity


class MigrationCredential(BaseEntity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationCredential"
