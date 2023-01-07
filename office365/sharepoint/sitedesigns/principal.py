from office365.sharepoint.base_entity import BaseEntity


class SiteDesignPrincipal(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Utilities.WebTemplateExtensions.SiteDesignPrincipal"
