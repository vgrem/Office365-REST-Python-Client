from office365.sharepoint.base_entity import BaseEntity


class HubSite(BaseEntity):
    """SharePoint hub sites help you meet the needs of your organization by connecting and organizing sites"""

    @property
    def id(self):
        """Gets the id of the hub site.

        :rtype: str or None
        """
        return self.properties.get("ID", None)

    @property
    def description(self):
        """Gets the description of the hub site type.

        :rtype: str or None
        """
        return self.properties.get("Description", None)

    @property
    def site_url(self):
        """Gets the url of the hub site.

        :rtype: str or None
        """
        return self.properties.get("SiteUrl", None)

    @property
    def targets(self):
        """List of security groups with access to join the hub site. Null if everyone has permission.

        :rtype: str or None
        """
        return self.properties.get("Targets", None)

    @property
    def title(self):
        """Gets the title of the hub site.

        :rtype: str or None
        """
        return self.properties.get("Title", None)

    @property
    def tenant_instance_id(self):
        """Gets The tenant instance ID in which the hub site is located.

        :rtype: str or None
        """
        return self.properties.get("TenantInstanceId", None)
