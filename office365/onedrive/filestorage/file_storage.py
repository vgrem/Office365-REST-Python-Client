from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.filestorage.container import FileStorageContainer
from office365.runtime.paths.resource_path import ResourcePath


class FileStorage(Entity):
    """Represents the structure of active and deleted fileStorageContainer objects."""

    @property
    def containers(self):
        """The collection of active fileStorageContainers"""
        return self.properties.get(
            "containers",
            EntityCollection(
                self.context,
                FileStorageContainer,
                ResourcePath("containers", self.resource_path),
            ),
        )
