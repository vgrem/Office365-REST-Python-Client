from office365.sharepoint.base_entity import BaseEntity


class SiteDesignRun(BaseEntity):

    @property
    def site_design_id(self):
        return self.properties.get("SiteDesignID", None)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Utilities.WebTemplateExtensions.SiteDesignRun"
