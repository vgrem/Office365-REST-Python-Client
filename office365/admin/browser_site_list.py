from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.admin.browser_shared_cookie import BrowserSharedCookie
    from office365.admin.browser_site import BrowserSite
    from office365.directory.identity_set import IdentitySet
    from office365.intune.browser.siteliststatus import BrowserSiteListStatus


class BrowserSiteList(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_by(self) -> IdentitySet:
        """Gets the lastModifiedBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("lastModifiedBy", IdentitySet())

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def published_by(self) -> IdentitySet:
        """Gets the publishedBy property"""
        from office365.directory.identity_set import IdentitySet

        return self.properties.get("publishedBy", IdentitySet())

    @property
    def published_date_time(self) -> Optional[datetime]:
        """Gets the publishedDateTime property"""
        return self.properties.get("publishedDateTime", datetime.min)

    @property
    def revision(self) -> Optional[str]:
        """Gets the revision property"""
        return self.properties.get("revision", None)

    @property
    def status(self) -> BrowserSiteListStatus:
        """Gets the status property"""
        from office365.intune.browser.siteliststatus import BrowserSiteListStatus

        return self.properties.get("status", BrowserSiteListStatus.draft)

    @property
    def shared_cookies(self) -> EntityCollection[BrowserSharedCookie]:
        """Gets the sharedCookies property"""
        from office365.admin.browser_shared_cookie import BrowserSharedCookie

        return self.properties.get(
            "sharedCookies",
            EntityCollection[BrowserSharedCookie](
                self.context, BrowserSharedCookie, ResourcePath("sharedCookies", self.resource_path)
            ),
        )

    @property
    def sites(self) -> EntityCollection[BrowserSite]:
        """Gets the sites property"""
        from office365.admin.browser_site import BrowserSite

        return self.properties.get(
            "sites", EntityCollection[BrowserSite](self.context, BrowserSite, ResourcePath("sites", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BrowserSiteList"
