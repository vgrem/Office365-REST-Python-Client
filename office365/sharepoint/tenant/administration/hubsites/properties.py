from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.tenant.administration.hubsites.permission import (
    HubSitePermission,
)


class HubSiteProperties(Entity):
    @property
    def permissions(self):
        return self.properties.get("Permissions", ClientValueCollection(HubSitePermission))

    @property
    def site_id(self) -> Optional[str]:
        """Returns the Site identifier"""
        return self.properties.get("SiteId", None)

    @property
    def property_ref_name(self):
        return "SiteId"

    @property
    def entity_type_name(self):  # type: ignore[override]
        return "Microsoft.Online.SharePoint.TenantAdministration.HubSiteProperties"

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def enable_permissions_sync(self) -> Optional[bool]:
        """Gets the EnablePermissionsSync property"""
        return self.properties.get("EnablePermissionsSync", None)

    @property
    def hide_name_in_navigation(self) -> Optional[bool]:
        """Gets the HideNameInNavigation property"""
        return self.properties.get("HideNameInNavigation", None)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def logo_url(self) -> Optional[str]:
        """Gets the LogoUrl property"""
        return self.properties.get("LogoUrl", None)

    @property
    def parent_hub_site_id(self) -> Optional[UUID]:
        """Gets the ParentHubSiteId property"""
        return self.properties.get("ParentHubSiteId", None)

    @property
    def requires_join_approval(self) -> Optional[bool]:
        """Gets the RequiresJoinApproval property"""
        return self.properties.get("RequiresJoinApproval", None)

    @property
    def site_design_id(self) -> Optional[UUID]:
        """Gets the SiteDesignId property"""
        return self.properties.get("SiteDesignId", None)

    @property
    def site_url(self) -> Optional[str]:
        """Gets the SiteUrl property"""
        return self.properties.get("SiteUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)
