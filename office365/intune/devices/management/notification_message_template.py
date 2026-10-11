from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.management.localized_notification_message import (
        LocalizedNotificationMessage,
    )
    from office365.intune.devices.management.notificationtemplatebrandingoptions import (
        NotificationTemplateBrandingOptions,
    )


class NotificationMessageTemplate(Entity):
    @property
    def branding_options(self) -> NotificationTemplateBrandingOptions:
        """Gets the brandingOptions property"""
        from office365.intune.devices.management.notificationtemplatebrandingoptions import (
            NotificationTemplateBrandingOptions,
        )

        return self.properties.get("brandingOptions", NotificationTemplateBrandingOptions.none)

    @property
    def default_locale(self) -> Optional[str]:
        """Gets the defaultLocale property"""
        return self.properties.get("defaultLocale", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def role_scope_tag_ids(self) -> StringCollection:
        """Gets the roleScopeTagIds property"""
        return self.properties.get("roleScopeTagIds", StringCollection())

    @property
    def localized_notification_messages(self) -> EntityCollection[LocalizedNotificationMessage]:
        """Gets the localizedNotificationMessages property"""
        from office365.intune.devices.management.localized_notification_message import (
            LocalizedNotificationMessage,
        )

        return self.properties.get(
            "localizedNotificationMessages",
            EntityCollection[LocalizedNotificationMessage](
                self.context,
                LocalizedNotificationMessage,
                ResourcePath("localizedNotificationMessages", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.NotificationMessageTemplate"
