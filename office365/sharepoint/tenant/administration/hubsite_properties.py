from office365.sharepoint.base_entity import BaseEntity


class HubSiteProperties(BaseEntity):

    @property
    def site_id(self):
        """
        Returns the Site identifier

        :rtype: str or None
        """
        return self.properties.get("SiteId", None)
