from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.sitedesigns.app_settings_in_teams import (
        AppSettingsInTeams,
    )
    from office365.sharepoint.viva.dashboard.item import DashboardItem
    from office365.sharepoint.viva.pivotitem import PivotItem


class AppConfiguration(Entity):
    @property
    def app_settings_in_teams(self) -> AppSettingsInTeams:
        """Gets the AppSettingsInTeams property"""
        from office365.sharepoint.sitedesigns.app_settings_in_teams import (
            AppSettingsInTeams,
        )

        return self.properties.get("AppSettingsInTeams", AppSettingsInTeams())

    @property
    def dashboard_items(self) -> ClientValueCollection[DashboardItem]:
        """Gets the DashboardItems property"""
        from office365.sharepoint.viva.dashboard.item import DashboardItem

        return self.properties.get("DashboardItems", ClientValueCollection[DashboardItem](DashboardItem))

    @property
    def pivot_items(self) -> ClientValueCollection[PivotItem]:
        """Gets the PivotItems property"""
        from office365.sharepoint.viva.pivotitem import PivotItem

        return self.properties.get("PivotItems", ClientValueCollection[PivotItem](PivotItem))
