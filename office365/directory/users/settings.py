from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.users.insights_settings import UserInsightsSettings
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.schedule.shifts.preferences import ShiftPreferences

if TYPE_CHECKING:
    from office365.common.exchange_settings import ExchangeSettings
    from office365.directory.users.storage import UserStorage
    from office365.directory.users.windows_setting import WindowsSetting
    from office365.directory.users.work_hours_and_locations_setting import (
        WorkHoursAndLocationsSetting,
    )


class UserSettings(Entity):
    """The current user settings for content discovery."""

    @property
    def contribution_to_content_discovery_as_organization_disabled(self) -> Optional[bool]:
        """Reflects the organization level setting controlling delegate access to the trending API.
        When set to true, the organization doesn't have access to Office Delve. The relevancy of the content
        displayed in Microsoft 365, for example in Suggested sites in SharePoint Home and the Discover view in
        OneDrive for work or school is affected for the whole organization. This setting is read-only and can only
        be changed by administrators in the SharePoint admin center."""
        return self.properties.get("contributionToContentDiscoveryAsOrganizationDisabled", None)

    @property
    def contribution_to_content_discovery_disabled(self) -> Optional[bool]:
        """When set to true, the delegate access to the user's trending API is disabled.
        When set to true, documents in the user's Office Delve are disabled. When set to true, the relevancy of
        the content displayed in Microsoft 365, for example in Suggested sites in SharePoint Home and the
        Discover view in OneDrive for work or school is affected. Users can control this setting in Office Delve
        """
        return self.properties.get("contributionToContentDiscoveryDisabled", None)

    @odata(name="itemInsights")
    @property
    def item_insights(self) -> UserInsightsSettings:
        """The user's settings for the visibility of meeting hour insights, and insights derived between
        a user and other items in Microsoft 365, such as documents or sites.
        Get userInsightsSettings through this navigation property."""
        return self.properties.get(
            "itemInsights", UserInsightsSettings(self.context, ResourcePath("itemInsights", self.resource_path))
        )

    @odata(name="shiftPreferences")
    @property
    def shift_preferences(self) -> ShiftPreferences:
        return self.properties.get(
            "shiftPreferences", ShiftPreferences(self.context, ResourcePath("shiftPreferences", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserSettings"

    @property
    def exchange(self) -> ExchangeSettings:
        """Gets the exchange property"""
        from office365.common.exchange_settings import ExchangeSettings

        return self.properties.get(
            "exchange", ExchangeSettings(self.context, ResourcePath("exchange", self.resource_path))
        )

    @property
    def windows(self) -> EntityCollection[WindowsSetting]:
        """Gets the windows property"""
        from office365.directory.users.windows_setting import WindowsSetting

        return self.properties.get(
            "windows",
            EntityCollection[WindowsSetting](self.context, WindowsSetting, ResourcePath("windows", self.resource_path)),
        )

    @property
    def storage(self) -> UserStorage:
        """Gets the storage property"""
        from office365.directory.users.storage import UserStorage

        return self.properties.get("storage", UserStorage(self.context, ResourcePath("storage", self.resource_path)))

    @property
    def work_hours_and_locations(self) -> WorkHoursAndLocationsSetting:
        """Gets the workHoursAndLocations property"""
        from office365.directory.users.work_hours_and_locations_setting import (
            WorkHoursAndLocationsSetting,
        )

        return self.properties.get(
            "workHoursAndLocations",
            WorkHoursAndLocationsSetting(self.context, ResourcePath("workHoursAndLocations", self.resource_path)),
        )
