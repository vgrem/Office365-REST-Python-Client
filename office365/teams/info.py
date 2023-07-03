from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class TeamInfo(Entity):
    """Represents a team with basic information."""

    @property
    def display_name(self):
        """
        The name of the team.
        :rtype: str or None
        """
        return self.properties.get('displayName', None)

    @property
    def team(self):
        from office365.teams.team import Team
        return self.properties.get('team',
                                   Team(self.context, ResourcePath("team", self.resource_path)))
