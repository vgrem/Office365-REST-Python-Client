from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.backuprestore.restoresessions.browser_shared_cookie_history import (
        BrowserSharedCookieHistory,
    )
    from office365.directory.identity_set import IdentitySet
    from office365.intune.browser.sharedcookiesourceenvironment import (
        BrowserSharedCookieSourceEnvironment,
    )
    from office365.intune.browser.sharedcookiestatus import BrowserSharedCookieStatus


class BrowserSharedCookie(Entity):
    @property
    def comment(self) -> Optional[str]:
        """Gets the comment property"""
        return self.properties.get("comment", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def deleted_date_time(self) -> Optional[datetime]:
        """Gets the deletedDateTime property"""
        return self.properties.get("deletedDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def history(self) -> ClientValueCollection[BrowserSharedCookieHistory]:
        """Gets the history property"""
        from office365.backuprestore.restoresessions.browser_shared_cookie_history import (
            BrowserSharedCookieHistory,
        )

        return self.properties.get(
            "history", ClientValueCollection[BrowserSharedCookieHistory](BrowserSharedCookieHistory)
        )

    @property
    def host_only(self) -> Optional[bool]:
        """Gets the hostOnly property"""
        return self.properties.get("hostOnly", None)

    @property
    def host_or_domain(self) -> Optional[str]:
        """Gets the hostOrDomain property"""
        return self.properties.get("hostOrDomain", None)

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
    def path(self) -> Optional[str]:
        """Gets the path property"""
        return self.properties.get("path", None)

    @property
    def source_environment(self) -> BrowserSharedCookieSourceEnvironment:
        """Gets the sourceEnvironment property"""
        from office365.intune.browser.sharedcookiesourceenvironment import (
            BrowserSharedCookieSourceEnvironment,
        )

        return self.properties.get("sourceEnvironment", BrowserSharedCookieSourceEnvironment.microsoftEdge)

    @property
    def status(self) -> BrowserSharedCookieStatus:
        """Gets the status property"""
        from office365.intune.browser.sharedcookiestatus import (
            BrowserSharedCookieStatus,
        )

        return self.properties.get("status", BrowserSharedCookieStatus.published)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BrowserSharedCookie"
