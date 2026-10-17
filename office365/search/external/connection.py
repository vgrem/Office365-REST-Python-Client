from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.search.external.configuration import Configuration
from office365.search.external.search_settings import SearchSettings

if TYPE_CHECKING:
    from office365.externalconnectors.activity_settings import ActivitySettings
    from office365.externalconnectors.connection_operation import ConnectionOperation
    from office365.externalconnectors.connectionstate import ConnectionState
    from office365.externalconnectors.content_category import ContentCategory
    from office365.externalconnectors.external_group import ExternalGroup
    from office365.externalconnectors.schema import Schema
    from office365.search.external.item import ExternalItem


class ExternalConnection(Entity):
    """A logical container to add content from an external source into Microsoft Graph."""

    @property
    def configuration(self):
        """
        Specifies additional application IDs that are allowed to manage the connection and to index
        content in the connection. Optional.
        """
        return self.properties.get("configuration", Configuration())

    @property
    def search_settings(self):
        """
        The settings configuring the search experience for content in this connection,
        such as the display templates for search results.
        """
        return self.properties.get("searchSettings", SearchSettings())

    @property
    def entity_type_name(self):
        return "microsoft.graph.externalConnectors.externalConnection"

    @property
    def activity_settings(self) -> Optional[ActivitySettings]:
        """Gets the activitySettings property"""
        return self.properties.get("activitySettings", None)

    @property
    def connector_id(self) -> Optional[str]:
        """Gets the connectorId property"""
        return self.properties.get("connectorId", None)

    @property
    def content_category(self) -> ContentCategory:
        """Gets the contentCategory property"""
        from office365.externalconnectors.content_category import ContentCategory

        return self.properties.get("contentCategory", ContentCategory.uncategorized)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def state(self) -> Optional[ConnectionState]:
        """Gets the state property"""
        return self.properties.get("state", None)

    @property
    def groups(self) -> EntityCollection[ExternalGroup]:
        """Gets the groups property"""
        from office365.externalconnectors.external_group import ExternalGroup

        return self.properties.get(
            "groups",
            EntityCollection[ExternalGroup](self.context, ExternalGroup, ResourcePath("groups", self.resource_path)),
        )

    @property
    def items(self) -> EntityCollection[ExternalItem]:
        """Gets the items property"""
        from office365.search.external.item import ExternalItem

        return self.properties.get(
            "items",
            EntityCollection[ExternalItem](self.context, ExternalItem, ResourcePath("items", self.resource_path)),
        )

    @property
    def operations(self) -> EntityCollection[ConnectionOperation]:
        """Gets the operations property"""
        from office365.externalconnectors.connection_operation import (
            ConnectionOperation,
        )

        return self.properties.get(
            "operations",
            EntityCollection[ConnectionOperation](
                self.context, ConnectionOperation, ResourcePath("operations", self.resource_path)
            ),
        )

    @property
    def schema(self) -> Schema:
        """Gets the schema property"""
        from office365.externalconnectors.schema import Schema

        return self.properties.get("schema", Schema(self.context, ResourcePath("schema", self.resource_path)))
