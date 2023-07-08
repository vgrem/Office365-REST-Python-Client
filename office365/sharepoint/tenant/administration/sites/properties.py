from office365.runtime.paths.key import KeyPath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.deny_add_and_customize_pages_status import \
    DenyAddAndCustomizePagesStatus


class SiteProperties(BaseEntity):
    """Contains a property bag of information about a site."""

    @staticmethod
    def clear_sharing_lock_down(context, site_url):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint client service
        :param str site_url:
        """
        payload = {"siteUrl": site_url}
        binding_type = SiteProperties(context)
        qry = ServiceOperationQuery(binding_type, "ClearSharingLockDown", None, payload, None, None, True)
        context.add_query(qry)
        return binding_type

    def update(self):
        """Updates the site collection properties with the new properties specified in the SiteProperties object."""

        site = Site(self.context)
        site.set_property("__siteUrl", self.url)

        def _site_loaded(return_type):
            self._resource_path = KeyPath(site.id, self.parent_collection.resource_path)
            super(SiteProperties, self).update()
        self.context.load(site, after_loaded=_site_loaded)
        return self

    @property
    def deny_add_and_customize_pages(self):
        """
        Represents the status of the [DenyAddAndCustomizePages] feature on a site collection.
        """
        return self.properties.get("DenyAddAndCustomizePages", DenyAddAndCustomizePagesStatus.Unknown)

    @deny_add_and_customize_pages.setter
    def deny_add_and_customize_pages(self, value):
        """
        Sets the status of the [DenyAddAndCustomizePages] feature on a site collection.

        :param int value:
        """
        self.set_property("DenyAddAndCustomizePages", value)

    @property
    def owner_login_name(self):
        """
        :rtype: str
        """
        return self.properties.get('OwnerLoginName', None)

    @property
    def webs_count(self):
        """
        Gets the number of Web objects in the site.
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

    @sharing_capability.setter
    def sharing_capability(self, value):
        """
        Sets the level of sharing for the site.
        :type value: int
        """
        self.set_property('SharingCapability', value)

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
            self._resource_path = ServiceOperationPath(self.entity_type_name, {"Url": value})
        return self
