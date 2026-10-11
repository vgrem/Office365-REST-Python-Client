from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.apps.app import TeamsApp
from office365.teams.tabs.configuration import TeamsTabConfiguration


class TeamsTab(Entity):
    """
    A teamsTab is a tab that's pinned (attached) to a channel within a team.
    """

    @odata(name="teamsApp")
    @property
    def teams_app(self) -> TeamsApp:
        """The application that is linked to the tab. This cannot be changed after tab creation."""
        return self.properties.get(
            "teamsApp",
            TeamsApp(self.context, ResourcePath("teamsApp", self.resource_path)),
        )

    @property
    def configuration(self) -> TeamsTabConfiguration:
        """
        Container for custom settings applied to a tab. The tab is considered configured only once this property is set.
        """
        return self.properties.get("configuration", TeamsTabConfiguration())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeamsTab"
