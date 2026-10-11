from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.configurations.ios.home_screen_item import (
        IosHomeScreenItem,
    )
    from office365.intune.devices.configurations.ios.home_screen_page import (
        IosHomeScreenPage,
    )
    from office365.intune.devices.configurations.ios.notification_settings import (
        IosNotificationSettings,
    )


class IosDeviceFeaturesConfiguration(Entity):
    @property
    def asset_tag_template(self) -> Optional[str]:
        """Gets the assetTagTemplate property"""
        return self.properties.get("assetTagTemplate", None)

    @property
    def home_screen_dock_icons(self) -> ClientValueCollection[IosHomeScreenItem]:
        """Gets the homeScreenDockIcons property"""
        from office365.intune.devices.configurations.ios.home_screen_item import (
            IosHomeScreenItem,
        )

        return self.properties.get("homeScreenDockIcons", ClientValueCollection[IosHomeScreenItem](IosHomeScreenItem))

    @property
    def home_screen_pages(self) -> ClientValueCollection[IosHomeScreenPage]:
        """Gets the homeScreenPages property"""
        from office365.intune.devices.configurations.ios.home_screen_page import (
            IosHomeScreenPage,
        )

        return self.properties.get("homeScreenPages", ClientValueCollection[IosHomeScreenPage](IosHomeScreenPage))

    @property
    def lock_screen_footnote(self) -> Optional[str]:
        """Gets the lockScreenFootnote property"""
        return self.properties.get("lockScreenFootnote", None)

    @property
    def notification_settings(self) -> ClientValueCollection[IosNotificationSettings]:
        """Gets the notificationSettings property"""
        from office365.intune.devices.configurations.ios.notification_settings import (
            IosNotificationSettings,
        )

        return self.properties.get(
            "notificationSettings", ClientValueCollection[IosNotificationSettings](IosNotificationSettings)
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosDeviceFeaturesConfiguration"
