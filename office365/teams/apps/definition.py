from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.teams.bots.teamwork_bot import TeamworkBot

if TYPE_CHECKING:
    from office365.teams.apps.authorization import TeamsAppAuthorization
    from office365.teams.apps.publishingstate import TeamsAppPublishingState


class TeamsAppDefinition(Entity):
    """Represents the details of a version of a teamsApp."""

    @property
    def bot(self) -> TeamworkBot:
        """The details of the bot specified in the Teams app manifest."""
        return self.properties.get("bot", TeamworkBot(self.context, ResourcePath("bot", self.resource_path)))

    @odata(name="createdBy")
    @property
    def created_by(self) -> IdentitySet:
        """Identity of the user, device, or application which created the item."""
        return self.properties.get("createdBy", IdentitySet())

    @property
    def description(self) -> str | None:
        """Verbose description of the application."""
        return self.properties.get("description", None)

    @odata(name="lastModifiedDateTime")
    @property
    def last_modified_datetime(self) -> datetime:
        """Gets date and time the teamsApp was last modified."""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def teams_app_id(self) -> str | None:
        """The ID from the Teams app manifest."""
        return self.properties.get("teamsAppId", None)

    @property
    def authorization(self) -> TeamsAppAuthorization:
        """Gets the authorization property"""
        from office365.teams.apps.authorization import TeamsAppAuthorization

        return self.properties.get("authorization", TeamsAppAuthorization())

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def publishing_state(self) -> TeamsAppPublishingState:
        """Gets the publishingState property"""
        from office365.teams.apps.publishingstate import TeamsAppPublishingState

        return self.properties.get("publishingState", TeamsAppPublishingState.submitted)

    @property
    def short_description(self) -> Optional[str]:
        """Gets the shortDescription property"""
        return self.properties.get("shortDescription", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TeamsAppDefinition"
