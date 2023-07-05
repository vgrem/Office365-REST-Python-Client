from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.search.external.connection import ExternalConnection
from office365.runtime.paths.resource_path import ResourcePath


class External(Entity):
    """A logical container  for external sources."""

    @property
    def connections(self):
        """Get a list of the externalConnection objects and their properties."""
        return self.properties.get('connections',
                                   EntityCollection(self.context, ExternalConnection,
                                                    ResourcePath("connections", self.resource_path)))

