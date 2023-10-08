from office365.sharepoint.entity import Entity


class AppDetails(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Packaging.AppDetails"
