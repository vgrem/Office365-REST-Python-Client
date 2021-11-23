from office365.directory.identities.identity_set import IdentitySet
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.bots.teamwork_bot import TeamworkBot


class TeamsAppDefinition(Entity):
    """Represents the details of a version of a teamsApp."""

    @property
    def bot(self):
        """The details of the bot specified in the Teams app manifest."""
        return self.get_property('bot',
                                 TeamworkBot(self.context, ResourcePath("bot", self.resource_path)))

    @property
    def created_by(self):
        """Identity of the user, device, or application which created the item."""
        return self.properties.get('createdBy', IdentitySet())

    @property
    def description(self):
        """Verbose description of the application."""
        return self.properties.get('description', IdentitySet())
