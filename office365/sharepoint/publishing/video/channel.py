from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.publishing.search import Search
from office365.sharepoint.publishing.spotlightvideo import SpotlightVideo
from office365.sharepoint.publishing.video.item import VideoItem


class VideoChannel(Entity):
    def get_video_count(self):
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetVideoCount", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Publishing.VideoChannel"

    @property
    def can_administrate_by_current(self) -> Optional[bool]:
        """Gets the CanAdministrateByCurrent property"""
        return self.properties.get("CanAdministrateByCurrent", None)

    @property
    def can_edit_by_current(self) -> Optional[bool]:
        """Gets the CanEditByCurrent property"""
        return self.properties.get("CanEditByCurrent", None)

    @property
    def can_view_by_current(self) -> Optional[bool]:
        """Gets the CanViewByCurrent property"""
        return self.properties.get("CanViewByCurrent", None)

    @property
    def channel_page_url(self) -> Optional[str]:
        """Gets the ChannelPageUrl property"""
        return self.properties.get("ChannelPageUrl", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def download_url_visible_min_permission(self) -> Optional[int]:
        """Gets the DownloadUrlVisibleMinPermission property"""
        return self.properties.get("DownloadUrlVisibleMinPermission", None)

    @property
    def full_url(self) -> Optional[str]:
        """Gets the FullUrl property"""
        return self.properties.get("FullUrl", None)

    @property
    def id_(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the ServerRelativeUrl property"""
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def share_by_email_enabled(self) -> Optional[bool]:
        """Gets the ShareByEmailEnabled property"""
        return self.properties.get("ShareByEmailEnabled", None)

    @property
    def tile_html_color(self) -> Optional[str]:
        """Gets the TileHtmlColor property"""
        return self.properties.get("TileHtmlColor", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def yammer_default_group_id(self) -> Optional[int]:
        """Gets the YammerDefaultGroupId property"""
        return self.properties.get("YammerDefaultGroupId", None)

    @property
    def yammer_enabled(self) -> Optional[bool]:
        """Gets the YammerEnabled property"""
        return self.properties.get("YammerEnabled", None)

    @property
    def search(self) -> Search:
        """Gets the Search property"""
        return self.properties.get("Search", Search(self.context, ResourcePath("Search", self.resource_path)))

    @property
    def spotlight_videos(self) -> EntityCollection[SpotlightVideo]:
        """Gets the SpotlightVideos property"""
        return self.properties.get(
            "SpotlightVideos",
            EntityCollection[SpotlightVideo](
                self.context, SpotlightVideo, ResourcePath("SpotlightVideos", self.resource_path)
            ),
        )

    @property
    def videos(self) -> EntityCollection[VideoItem]:
        """Gets the Videos property"""
        return self.properties.get(
            "Videos", EntityCollection[VideoItem](self.context, VideoItem, ResourcePath("Videos", self.resource_path))
        )

    def get_channel_page_url(self, view_mode: int) -> ClientResult[str]:
        """GetChannelPageUrl operation.

        Args:
            view_mode (int): viewMode parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetChannelPageUrl", [view_mode], return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
