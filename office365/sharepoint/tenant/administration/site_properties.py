from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.internal.paths.entity_resource import EntityResourcePath


class SiteProperties(BaseEntity):
    """Contains a property bag of information about a site."""

    def __init__(self, context):
        super(SiteProperties, self).__init__(context)

    def update(self):
        """Updates the site collection properties with the new properties specified in the SiteProperties object."""
        def _update():
            super(SiteProperties, self).update()

        self._ensure_resource_path(_update)
        return self

    def set_property(self, name, value, persist_changes=True):
        super(SiteProperties, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "Url" and self._resource_path is None:
            pass

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
            - ExternalUserAndGuestSharing (default) - External user sharing (share by email) and guest link sharing are both enabled.
            - Disabled - External user sharing (share by email) and guest link sharing are both disabled.
            - ExternalUserSharingOnly - External user sharing (share by email) is enabled, but guest link sharing is disabled.
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

    def _ensure_resource_path(self, action):
        """
        :type action: () -> None
        """
        def _ensure_site_url():
            ctx = self.context.clone(self.url)
            site = ctx.site.select(["Id"]).get().execute_query()
            self._resource_path = EntityResourcePath(site.id, self._parent_collection.resource_path)
            action()

        if self._resource_path is None:
            self.ensure_property("Url", _ensure_site_url)
        else:
            action()
        return self
