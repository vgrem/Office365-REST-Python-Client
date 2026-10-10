from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.publishing.video.channel_collection import (
    VideoChannelCollection,
)

if TYPE_CHECKING:
    from office365.sharepoint.publishing.search import Search
    from office365.sharepoint.publishing.spotlightchannel import SpotlightChannel
    from office365.sharepoint.publishing.spotlightvideo import SpotlightVideo
    from office365.sharepoint.publishing.video.channel import VideoChannel


class VideoServiceManager(Entity):
    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.Publishing.VideoServiceManager"))

    def get_channels(self, start_index=0, limit=None) -> VideoChannelCollection:
        return_type = VideoChannelCollection(self.context)
        params = {"startIndex": start_index, "limit": limit}
        qry = ServiceOperationQuery(self, "GetChannels", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def automatic_migration_type(self) -> Optional[str]:
        """Gets the AutomaticMigrationType property"""
        return self.properties.get("AutomaticMigrationType", None)

    @property
    def can_administrate_portal_by_current(self) -> Optional[bool]:
        """Gets the CanAdministratePortalByCurrent property"""
        return self.properties.get("CanAdministratePortalByCurrent", None)

    @property
    def can_create_channels_by_current(self) -> Optional[bool]:
        """Gets the CanCreateChannelsByCurrent property"""
        return self.properties.get("CanCreateChannelsByCurrent", None)

    @property
    def can_view_portal_by_current(self) -> Optional[bool]:
        """Gets the CanViewPortalByCurrent property"""
        return self.properties.get("CanViewPortalByCurrent", None)

    @property
    def upload_guidelines_link(self) -> Optional[str]:
        """Gets the UploadGuidelinesLink property"""
        return self.properties.get("UploadGuidelinesLink", None)

    @property
    def video_guidelines_link(self) -> Optional[str]:
        """Gets the VideoGuidelinesLink property"""
        return self.properties.get("VideoGuidelinesLink", None)

    @property
    def entity_type_name(self):
        return "SP.Publishing.VideoServiceManager"

    @property
    def can_edit_channels(self) -> EntityCollection[VideoChannel]:
        """Gets the CanEditChannels property"""
        from office365.sharepoint.publishing.video.channel import VideoChannel

        return self.properties.get(
            "CanEditChannels",
            EntityCollection[VideoChannel](
                self.context, VideoChannel, ResourcePath("CanEditChannels", self.resource_path)
            ),
        )

    @property
    def channels(self) -> EntityCollection[VideoChannel]:
        """Gets the Channels property"""
        from office365.sharepoint.publishing.video.channel import VideoChannel

        return self.properties.get(
            "Channels",
            EntityCollection[VideoChannel](self.context, VideoChannel, ResourcePath("Channels", self.resource_path)),
        )

    @property
    def search(self) -> Search:
        """Gets the Search property"""
        from office365.sharepoint.publishing.search import Search

        return self.properties.get("Search", Search(self.context, ResourcePath("Search", self.resource_path)))

    @property
    def spotlight_channels(self) -> EntityCollection[SpotlightChannel]:
        """Gets the SpotlightChannels property"""
        from office365.sharepoint.publishing.spotlightchannel import SpotlightChannel

        return self.properties.get(
            "SpotlightChannels",
            EntityCollection[SpotlightChannel](
                self.context, SpotlightChannel, ResourcePath("SpotlightChannels", self.resource_path)
            ),
        )

    @property
    def spotlight_videos(self) -> EntityCollection[SpotlightVideo]:
        """Gets the SpotlightVideos property"""
        from office365.sharepoint.publishing.spotlightvideo import SpotlightVideo

        return self.properties.get(
            "SpotlightVideos",
            EntityCollection[SpotlightVideo](
                self.context, SpotlightVideo, ResourcePath("SpotlightVideos", self.resource_path)
            ),
        )
