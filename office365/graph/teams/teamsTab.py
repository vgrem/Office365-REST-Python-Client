from office365.graph.entity import Entity
from office365.graph.teams.teamsApp import TeamsApp
from office365.graph.teams.teamsTabConfiguration import TeamsTabConfiguration
from office365.runtime.resource_path import ResourcePath


class TeamsTab(Entity):
    """
    A teamsTab is a tab that's pinned (attached) to a channel within a team.
    """

    @property
    def teamsApp(self):
        """The application that is linked to the tab. This cannot be changed after tab creation."""
        return self.properties.get('teamsApp',
                                   TeamsApp(self.context, ResourcePath("teamsApp", self.resource_path)))

    @property
    def configuration(self):
        """
        Container for custom settings applied to a tab. The tab is considered configured only once this property is set.
        :rtype: TeamsTabConfiguration
        """
        return self.properties.get("configuration", TeamsTabConfiguration())
