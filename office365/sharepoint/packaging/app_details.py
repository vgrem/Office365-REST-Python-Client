from office365.sharepoint.base_entity import BaseEntity


class AppDetails(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Packaging.AppDetails"
