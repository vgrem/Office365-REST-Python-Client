from office365.sharepoint.base_entity import BaseEntity


class TeamsPackageDownload(BaseEntity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Marketplace.CorporateCuratedGallery.TeamsPackageDownload"
