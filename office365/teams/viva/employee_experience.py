from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.viva.learning_provider import LearningProvider


class EmployeeExperience(Entity):
    """Represents a container that exposes navigation properties for employee experience resources."""

    @property
    def learning_providers(self):
        """A collection of learning providers."""
        return self.properties.get('learningProviders',
                                   EntityCollection(self.context, LearningProvider,
                                                    ResourcePath("learningProviders", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "learningProviders": self.learning_providers,
            }
            default_value = property_mapping.get(name, None)
        return super(EmployeeExperience, self).get_property(name, default_value)
