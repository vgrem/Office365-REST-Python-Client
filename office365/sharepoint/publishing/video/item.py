from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.publishing.itemviewsanalyticsdata import (
    ItemViewsAnalyticsData,
)
from office365.sharepoint.publishing.viewprogressanalyticsdata import (
    ViewProgressAnalyticsData,
)


class VideoItem(Entity):
    def get_video_embed_code(self, width, height, autoplay=True, show_info=True, make_responsive=True):
        """Args:
        width (int):
        height (int):
        autoplay (bool):
        show_info (bool):
        make_responsive (bool):
        """
        return_type = ClientResult(self.context)
        params = {
            "width": width,
            "height": height,
            "autoplay": autoplay,
            "showInfo": show_info,
            "makeResponsive": make_responsive,
        }
        qry = ServiceOperationQuery(self, "GetVideoEmbedCode", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_video_owner(self, owner_id):
        """Args:
        owner_id (int):
        """
        payload = {"id": owner_id}
        qry = ServiceOperationQuery(self, "SetVideoOwner", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "SP.Publishing.VideoItem"

    @property
    def channel_id(self) -> Optional[UUID]:
        """Gets the ChannelID property"""
        return self.properties.get("ChannelID", None)

    @property
    def created_date(self) -> Optional[datetime]:
        """Gets the CreatedDate property"""
        return self.properties.get("CreatedDate", datetime.min)

    @property
    def default_embed_code(self) -> Optional[str]:
        """Gets the DefaultEmbedCode property"""
        return self.properties.get("DefaultEmbedCode", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def display_form_url(self) -> Optional[str]:
        """Gets the DisplayFormUrl property"""
        return self.properties.get("DisplayFormUrl", None)

    @property
    def file_name(self) -> Optional[str]:
        """Gets the FileName property"""
        return self.properties.get("FileName", None)

    @property
    def owner_name(self) -> Optional[str]:
        """Gets the OwnerName property"""
        return self.properties.get("OwnerName", None)

    @property
    def player_page_url(self) -> Optional[str]:
        """Gets the PlayerPageUrl property"""
        return self.properties.get("PlayerPageUrl", None)

    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the ServerRelativeUrl property"""
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def thumbnail_selection(self) -> Optional[int]:
        """Gets the ThumbnailSelection property"""
        return self.properties.get("ThumbnailSelection", None)

    @property
    def thumbnail_url(self) -> Optional[str]:
        """Gets the ThumbnailUrl property"""
        return self.properties.get("ThumbnailUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def id_(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def url(self) -> Optional[str]:
        """Gets the Url property"""
        return self.properties.get("Url", None)

    @property
    def video_download_url(self) -> Optional[str]:
        """Gets the VideoDownloadUrl property"""
        return self.properties.get("VideoDownloadUrl", None)

    @property
    def video_duration_in_seconds(self) -> Optional[int]:
        """Gets the VideoDurationInSeconds property"""
        return self.properties.get("VideoDurationInSeconds", None)

    @property
    def video_processing_status(self) -> Optional[int]:
        """Gets the VideoProcessingStatus property"""
        return self.properties.get("VideoProcessingStatus", None)

    @property
    def view_count(self) -> Optional[int]:
        """Gets the ViewCount property"""
        return self.properties.get("ViewCount", None)

    @property
    def yammer_object_url(self) -> Optional[str]:
        """Gets the YammerObjectUrl property"""
        return self.properties.get("YammerObjectUrl", None)

    @property
    def author(self) -> User:
        """Gets the Author property"""
        return self.properties.get("Author", User(self.context, ResourcePath("Author", self.resource_path)))

    @property
    def owner(self) -> User:
        """Gets the Owner property"""
        return self.properties.get("Owner", User(self.context, ResourcePath("Owner", self.resource_path)))

    @property
    def people_in_media(self) -> EntityCollection[User]:
        """Gets the PeopleInMedia property"""
        return self.properties.get(
            "PeopleInMedia",
            EntityCollection[User](self.context, User, ResourcePath("PeopleInMedia", self.resource_path)),
        )

    def custom_thumbnail(self) -> ClientResult[bytes]:
        """CustomThumbnail operation."""
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "CustomThumbnail", [], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def get_playback_url(self, video_format: int) -> ClientResult[str]:
        """GetPlaybackUrl operation.

        Args:
            video_format (int): videoFormat parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetPlaybackUrl", [video_format], return_type)
        self.context.add_query(qry)
        return return_type

    def get_streaming_key_access_token(self) -> ClientResult[str]:
        """GetStreamingKeyAccessToken operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetStreamingKeyAccessToken", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_video_detailed_view_count(self) -> ClientResult[ItemViewsAnalyticsData]:
        """GetVideoDetailedViewCount operation."""
        return_type = ClientResult(self.context, ItemViewsAnalyticsData())
        qry = FunctionQuery(self, "GetVideoDetailedViewCount", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_video_view_progress_count(self) -> ClientResult[ClientValueCollection[ViewProgressAnalyticsData]]:
        """GetVideoViewProgressCount operation."""
        return_type = ClientResult(self.context, ClientValueCollection[ViewProgressAnalyticsData]())
        qry = FunctionQuery(self, "GetVideoViewProgressCount", [], return_type)
        self.context.add_query(qry)
        return return_type

    def increment_video_view_progress_count(self, percentage_viewed: int) -> Self:
        """IncrementVideoViewProgressCount operation.

        Args:
            percentage_viewed (int): percentageViewed parameter
        """
        qry = ServiceOperationQuery(
            self, "IncrementVideoViewProgressCount", None, {"percentageViewed": percentage_viewed}, None, None
        )
        self.context.add_query(qry)
        return self

    def increment_view_count(self, view_origin: int) -> Self:
        """IncrementViewCount operation.

        Args:
            view_origin (int): viewOrigin parameter
        """
        qry = ServiceOperationQuery(self, "IncrementViewCount", None, {"viewOrigin": view_origin}, None, None)
        self.context.add_query(qry)
        return self

    def set_people_in_media(self, login_names: list[str]) -> Self:
        """SetPeopleInMedia operation.

        Args:
            login_names (list[str]): loginNames parameter
        """
        qry = ServiceOperationQuery(
            self, "SetPeopleInMedia", None, {"loginNames": StringCollection(login_names)}, None, None
        )
        self.context.add_query(qry)
        return self

    def thumbnail_stream(self, preferred_width: int) -> ClientResult[bytes]:
        """ThumbnailStream operation.

        Args:
            preferred_width (int): preferredWidth parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "ThumbnailStream", [preferred_width], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def upload_custom_thumbnail(self, file_extension: str, custom_video_thumbnail: bytes) -> Self:
        """UploadCustomThumbnail operation.

        Args:
            file_extension (str): fileExtension parameter
            custom_video_thumbnail (bytes): customVideoThumbnail parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UploadCustomThumbnail",
            None,
            {"fileExtension": file_extension, "customVideoThumbnail": custom_video_thumbnail},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    @property
    def id(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)
