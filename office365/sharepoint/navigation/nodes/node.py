from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import GuidCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.translation.user_resource import UserResource

if TYPE_CHECKING:
    from office365.sharepoint.navigation.nodes.collection import (
        NavigationNodeCollection,
    )


class NavigationNode(Entity):
    """
    Represents the URL to a specific navigation node and provides access to properties and methods for
    manipulating the ordering of the navigation node in a navigation node collection.
    """

    def __str__(self):
        return self.title or self.entity_type_name

    def __repr__(self):
        return self.url or self.entity_type_name

    @property
    def id(self) -> int | None:
        """Gets the unique identifier of the navigation node."""
        return self.properties.get("Id", None)

    @property
    def children(self) -> NavigationNodeCollection:
        """Gets the collection of child nodes of the navigation node."""
        from office365.sharepoint.navigation.nodes.collection import (
            NavigationNodeCollection,
        )

        return self.properties.get(
            "Children",
            NavigationNodeCollection(self.context, ResourcePath("Children", self.resource_path)),
        )

    @property
    def title(self) -> str | None:
        """Gets a value that specifies the anchor text for the navigation node link."""
        return self.properties.get("Title", None)

    @title.setter
    def title(self, value: str) -> None:
        """Sets a value that specifies the anchor text for the navigation node link."""
        self.set_property("Title", value)

    @property
    def url(self) -> str | None:
        """Gets a value that specifies the URL stored with the navigation node."""
        return self.properties.get("Url", None)

    @url.setter
    def url(self, value: str) -> None:
        """Sets a value that specifies the URL stored with the navigation node."""
        self.set_property("Url", value)

    @property
    def is_visible(self) -> bool | None:
        """Gets a value that specifies the anchor text for the navigation node link."""
        return self.properties.get("isVisible", None)

    @property
    def is_external(self) -> bool | None:
        return self.properties.get("isExternal", None)

    @odata(name="TitleResource")
    @property
    def title_resource(self) -> UserResource:
        """Represents the title of this node."""
        return self.properties.get(
            "TitleResource",
            UserResource(self.context, ResourcePath("TitleResource", self.resource_path)),
        )

    @property
    def audience_ids(self) -> GuidCollection:
        """Gets the AudienceIds property"""
        return self.properties.get("AudienceIds", GuidCollection())

    @property
    def current_lcid(self) -> Optional[int]:
        """Gets the CurrentLCID property"""
        return self.properties.get("CurrentLCID", None)

    @property
    def is_doc_lib(self) -> Optional[bool]:
        """Gets the IsDocLib property"""
        return self.properties.get("IsDocLib", None)

    @property
    def list_template_type(self) -> Optional[int]:
        """Gets the ListTemplateType property"""
        return self.properties.get("ListTemplateType", None)
