from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.people.profile_card_property import ProfileCardProperty
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.admin.people.insights_settings import InsightsSettings
    from office365.admin.people.profile_property_setting import ProfilePropertySetting
    from office365.admin.people.profile_source import ProfileSource
    from office365.admin.people.pronouns_settings import PronounsSettings


class PeopleAdminSettings(Entity):
    """Represents a setting to control people-related admin settings in the tenant."""

    @odata(name="profileCardProperties")
    @property
    def profile_card_properties(self) -> EntityCollection[ProfileCardProperty]:
        """Contains a collection of the properties an administrator has defined as visible on the
        Microsoft 365 profile card."""
        return self.properties.get(
            "profileCardProperties",
            EntityCollection(
                self.context,
                ProfileCardProperty,
                ResourcePath("profileCardProperties", self.resource_path),
            ),
        )

    @property
    def item_insights(self) -> InsightsSettings:
        """Gets the itemInsights property"""
        from office365.admin.people.insights_settings import InsightsSettings

        return self.properties.get(
            "itemInsights", InsightsSettings(self.context, ResourcePath("itemInsights", self.resource_path))
        )

    @property
    def profile_property_settings(self) -> EntityCollection[ProfilePropertySetting]:
        """Gets the profilePropertySettings property"""
        from office365.admin.people.profile_property_setting import (
            ProfilePropertySetting,
        )

        return self.properties.get(
            "profilePropertySettings",
            EntityCollection[ProfilePropertySetting](
                self.context, ProfilePropertySetting, ResourcePath("profilePropertySettings", self.resource_path)
            ),
        )

    @property
    def profile_sources(self) -> EntityCollection[ProfileSource]:
        """Gets the profileSources property"""
        from office365.admin.people.profile_source import ProfileSource

        return self.properties.get(
            "profileSources",
            EntityCollection[ProfileSource](
                self.context, ProfileSource, ResourcePath("profileSources", self.resource_path)
            ),
        )

    @property
    def pronouns(self) -> PronounsSettings:
        """Gets the pronouns property"""
        from office365.admin.people.pronouns_settings import PronounsSettings

        return self.properties.get(
            "pronouns", PronounsSettings(self.context, ResourcePath("pronouns", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PeopleAdminSettings"
