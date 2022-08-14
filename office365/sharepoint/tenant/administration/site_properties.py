from office365.sharepoint.base_entity import BaseEntity


class SiteProperties(BaseEntity):
    """Contains a property bag of information about a site."""

    def update(self):
        """Updates the site collection properties with the new properties specified in the SiteProperties object."""
        def _ensure_site_loaded():
            ctx = self.context.clone(self.url)
            ctx.site.update()
        self.ensure_property("Url", _ensure_site_loaded)
        return self

    @property
    def owner_login_name(self):
        """
        :rtype: str
        """
        return self.properties.get('OwnerLoginName', None)

    @property
    def webs_count(self):
        """
        :rtype: int
        """
        return self.properties.get('WebsCount', None)

    @property
    def url(self):
        """
        Gets the URL of the site.

        :rtype: str
        """
        return self.properties.get('Url', None)

    @property
    def compatibility_level(self):
        """
        Gets the compatibility level of the site.

        :rtype: str
        """
        return self.properties.get('CompatibilityLevel', None)

    @property
    def lock_state(self):
        """
        Gets or sets the lock state of the site.

        :rtype: str
        """
        return self.properties.get('LockState', None)

    @property
    def sharing_capability(self):
        """
        Determines what level of sharing is available for the site.

        The valid values are:
            - ExternalUserAndGuestSharing (default) - External user sharing (share by email) and guest link sharing
                 are both enabled.
            - Disabled - External user sharing (share by email) and guest link sharing are both disabled.
            - ExternalUserSharingOnly - External user sharing (share by email) is enabled, but guest link sharing
                 is disabled.
            - ExistingExternalUserSharingOnly - Only guests already in your organization's directory.


        :rtype: int
        """
        return self.properties.get('SharingCapability', None)

    @property
    def time_zone_id(self):
        """
        Gets the time zone ID of the site.

        :rtype: str
        """
        return self.properties.get('TimeZoneId', None)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteProperties"

    def set_property(self, name, value, persist_changes=True):
        super(SiteProperties, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "Url" and self._resource_path is None:
            pass
