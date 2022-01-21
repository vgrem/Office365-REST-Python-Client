from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.apps.app_definition import TeamsAppDefinition


class TeamsApp(Entity):
    """Represents an app in the Microsoft Teams app catalog."""

    @property
    def app_definitions(self):
        """The details for each version of the app.

        :rtype: EntityCollection
        """
        return self.get_property('appDefinitions',
                                 EntityCollection(self.context, TeamsAppDefinition,
                                                  ResourcePath("appDefinitions", self.resource_path)))
