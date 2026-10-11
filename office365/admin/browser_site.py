from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.directory.identity_set import IdentitySet
    from office365.intune.browser.browser_site_history import BrowserSiteHistory
    from office365.intune.browser.sitecompatibilitymode import (
        BrowserSiteCompatibilityMode,
    )
    from office365.intune.browser.sitemergetype import BrowserSiteMergeType
    from office365.intune.browser.sitestatus import BrowserSiteStatus
    from office365.intune.browser.sitetargetenvironment import (
        BrowserSiteTargetEnvironment,
    )


class BrowserSite(Entity):
    @property
    def allow_redirect(self) -> Optional[bool]:
        """Gets the allowRedirect property"""
        return self.properties.get("allowRedirect", None)

    @property
    def comment(self) -> Optional[str]:
        """Gets the comment property"""
        return self.properties.get("comment", None)

    @property
    def compatibility_mode(self) -> BrowserSiteCompatibilityMode:
        """Gets the compatibilityMode property"""
        from office365.intune.browser.sitecompatibilitymode import (
            BrowserSiteCompatibilityMode,
        )

        return self.properties.get("compatibilityMode", BrowserSiteCompatibilityMode.default)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def deleted_date_time(self) -> Optional[datetime]:
        """Gets the deletedDateTime property"""
        return self.properties.get("deletedDateTime", datetime.min)

    @property
    def history(self) -> ClientValueCollection[BrowserSiteHistory]:
        """Gets the history property"""
        from office365.intune.browser.browser_site_history import BrowserSiteHistory

        return self.properties.get("history", ClientValueCollection[BrowserSiteHistory](BrowserSiteHistory))

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
    def merge_type(self) -> BrowserSiteMergeType:
        """Gets the mergeType property"""
        from office365.intune.browser.sitemergetype import BrowserSiteMergeType

        return self.properties.get("mergeType", BrowserSiteMergeType.noMerge)

    @property
    def status(self) -> BrowserSiteStatus:
        """Gets the status property"""
        from office365.intune.browser.sitestatus import BrowserSiteStatus

        return self.properties.get("status", BrowserSiteStatus.published)

    @property
    def target_environment(self) -> BrowserSiteTargetEnvironment:
        """Gets the targetEnvironment property"""
        from office365.intune.browser.sitetargetenvironment import (
            BrowserSiteTargetEnvironment,
        )

        return self.properties.get("targetEnvironment", BrowserSiteTargetEnvironment.internetExplorerMode)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BrowserSite"
