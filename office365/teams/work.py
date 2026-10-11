from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.deleted import DeletedTeam

if TYPE_CHECKING:
    from office365.teams.app_settings import TeamsAppSettings
    from office365.teams.chats.deleted import DeletedChat
    from office365.teams.workforce_integration import WorkforceIntegration


class Teamwork(Entity):
    """A container for the range of Microsoft Teams functionalities that are available for the organization."""

    @property
    def is_teams_enabled(self) -> Optional[bool]:
        """Indicates whether Microsoft Teams is enabled for the organization."""
        return self.properties.get("isTeamsEnabled", None)

    @property
    def region(self) -> Optional[str]:
        """Represents the region of the organization or the tenant.
        The region value can be any region supported by the Teams payload"""
        return self.properties.get("region", None)

    @property
    def deleted_teams(self) -> EntityCollection[DeletedTeam]:
        """The tags associated with the team."""
        return self.properties.get(
            "deletedTeams",
            EntityCollection(
                self.context,
                DeletedTeam,
                ResourcePath("deletedTeams", self.resource_path),
            ),
        )

    @property
    def workforce_integrations(self) -> EntityCollection[WorkforceIntegration]:
        """Gets the workforceIntegrations property"""
        from office365.teams.workforce_integration import WorkforceIntegration

        return self.properties.get(
            "workforceIntegrations",
            EntityCollection[WorkforceIntegration](
                self.context, WorkforceIntegration, ResourcePath("workforceIntegrations", self.resource_path)
            ),
        )

    @property
    def deleted_chats(self) -> EntityCollection[DeletedChat]:
        """Gets the deletedChats property"""
        from office365.teams.chats.deleted import DeletedChat

        return self.properties.get(
            "deletedChats",
            EntityCollection[DeletedChat](self.context, DeletedChat, ResourcePath("deletedChats", self.resource_path)),
        )

    @property
    def teams_app_settings(self) -> TeamsAppSettings:
        """Gets the teamsAppSettings property"""
        from office365.teams.app_settings import TeamsAppSettings

        return self.properties.get(
            "teamsAppSettings", TeamsAppSettings(self.context, ResourcePath("teamsAppSettings", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Teamwork"
