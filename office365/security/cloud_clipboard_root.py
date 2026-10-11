from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.security.cloud_clipboard_item import CloudClipboardItem


class CloudClipboardRoot(Entity):
    @property
    def items(self) -> EntityCollection[CloudClipboardItem]:
        """Gets the items property"""
        from office365.security.cloud_clipboard_item import CloudClipboardItem

        return self.properties.get(
            "items",
            EntityCollection[CloudClipboardItem](
                self.context, CloudClipboardItem, ResourcePath("items", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudClipboardRoot"
