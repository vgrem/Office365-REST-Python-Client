from office365.directory.directory_object import DirectoryObject
from office365.directory.extensions.extension import Extension
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class Organization(DirectoryObject):
    """
    The organization resource represents an instance of global settings and resources
    which operate and are provisioned at the tenant-level.
    """

    @property
    def extensions(self):
        """The collection of open extensions defined for the message. Nullable."""
        return self.properties.get('extensions',
                                   EntityCollection(self.context, Extension,
                                                    ResourcePath("extensions", self.resource_path)))
