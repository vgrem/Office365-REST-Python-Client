from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.publishing.video.item import VideoItem


class SpotlightVideo(Entity):
    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the ServerRelativeUrl property"""
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def url(self) -> Optional[str]:
        """Gets the Url property"""
        return self.properties.get("Url", None)

    @property
    def entity_type_name(self):
        return "SP.Publishing.SpotlightVideo"

    @property
    def id(self) -> Optional[int]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def video(self) -> VideoItem:
        """Gets the Video property"""
        from office365.sharepoint.publishing.video.item import VideoItem

        return self.properties.get("Video", VideoItem(self.context, ResourcePath("Video", self.resource_path)))
