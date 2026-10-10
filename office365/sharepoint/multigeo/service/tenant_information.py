from __future__ import annotations

from typing import Optional

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class TenantInformation(Entity):
    """ """

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.TenantInformation"

    @property
    def geo_location(self) -> Optional[str]:
        """Gets the GeoLocation property"""
        return self.properties.get("GeoLocation", None)

    @property
    def is_ib_enabled(self) -> Optional[bool]:
        """Gets the IsIBEnabled property"""
        return self.properties.get("IsIBEnabled", None)

    @property
    def my_site_host_domain(self) -> Optional[str]:
        """Gets the MySiteHostDomain property"""
        return self.properties.get("MySiteHostDomain", None)

    @property
    def portal_domain(self) -> Optional[str]:
        """Gets the PortalDomain property"""
        return self.properties.get("PortalDomain", None)

    @property
    def root_site_domain(self) -> Optional[str]:
        """Gets the RootSiteDomain property"""
        return self.properties.get("RootSiteDomain", None)

    @property
    def tenant_admin_domain(self) -> Optional[str]:
        """Gets the TenantAdminDomain property"""
        return self.properties.get("TenantAdminDomain", None)

    @property
    def vanity_domains(self) -> StringCollection:
        """Gets the VanityDomains property"""
        return self.properties.get("VanityDomains", StringCollection())
