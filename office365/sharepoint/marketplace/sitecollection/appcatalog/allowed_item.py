from office365.sharepoint.base_entity import BaseEntity


class SiteCollectionAppCatalogAllowedItem(BaseEntity):
    """An entry in the site collection app catalog allow list."""

    @property
    def site_id(self):
        """The ID of a site collection in the allow list.

        :rtype: str or None
        """
        return self.properties.get("SiteID", None)

    @property
    def absolute_url(self):
        """The absolute URL of a site collection in the allow list.

        :rtype: str or None
        """
        return self.properties.get("AbsoluteUrl", None)

    @property
    def property_ref_name(self):
        return "AbsoluteUrl"

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Marketplace.CorporateCuratedGallery.SiteCollectionAppCatalogAllowedItem"
