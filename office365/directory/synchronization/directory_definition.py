from datetime import datetime
from typing import Optional

from office365.directory.synchronization.directorydefinitiondiscoverabilities import DirectoryDefinitionDiscoverabilities
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.object_definition import ObjectDefinition


class DirectoryDefinition(Entity):
    """
    Provides the synchronization engine information about a directory and its objects. This resource tells the
    synchronization engine, for example, that the directory has objects named user and group, which attributes are
    supported for those objects, and the types for those attributes. In order for the object and attribute to
    participate in synchronization rules and object mappings, they must be defined as part of the directory definition.

    Directory definitions are updated as part of the synchronization schema.
    """

    @property
    def discoverabilities(self) -> DirectoryDefinitionDiscoverabilities:
        """Gets the discoverabilities property"""
        return self.properties.get("discoverabilities", DirectoryDefinitionDiscoverabilities.Unknown)

    @property
    def discovery_date_time(self) -> datetime:
        """Gets the discoveryDateTime property"""
        return self.properties.get("discoveryDateTime", datetime.min)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def objects(self) -> ClientValueCollection[ObjectDefinition]:
        """Gets the objects property"""
        return self.properties.get("objects", ClientValueCollection[ObjectDefinition](ObjectDefinition))

    @property
    def read_only(self) -> Optional[bool]:
        """Gets the readOnly property"""
        return self.properties.get("readOnly", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DirectoryDefinition"
