from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from office365.directory.synchronization.schema import SynchronizationSchema
from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.synchronization.metadata_entry import (
        SynchronizationMetadataEntry,
    )


class SynchronizationTemplate(Entity):
    """
    Provides pre-configured synchronization settings for a particular application. These settings will be used by
    default for any synchronization job that is based on the template. The application developer specifies the template;
    anyone can retrieve the template to see the default settings, including the synchronization schema.

    You can provide multiple templates for an application, and designate a default template. If multiple templates
    are available for the application you're interested in, seek application-specific guidance to determine which one
    best meets your needs.
    """

    @property
    def schema(self):
        """Default synchronization schema for the jobs based on this template."""
        return self.properties.get(
            "schema", SynchronizationSchema(self.context, ResourcePath("schema", self.resource_path))
        )

    @property
    def application_id(self) -> Optional[UUID]:
        """Gets the applicationId property"""
        return self.properties.get("applicationId", None)

    @property
    def default(self) -> Optional[bool]:
        """Gets the default property"""
        return self.properties.get("default", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def discoverable(self) -> Optional[bool]:
        """Gets the discoverable property"""
        return self.properties.get("discoverable", None)

    @property
    def factory_tag(self) -> Optional[str]:
        """Gets the factoryTag property"""
        return self.properties.get("factoryTag", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SynchronizationTemplate"

    @property
    def metadata(self) -> ClientValueCollection[SynchronizationMetadataEntry]:
        """Gets the metadata property"""
        from office365.directory.synchronization.metadata_entry import (
            SynchronizationMetadataEntry,
        )

        return self.properties.get(
            "metadata", ClientValueCollection[SynchronizationMetadataEntry](SynchronizationMetadataEntry)
        )
