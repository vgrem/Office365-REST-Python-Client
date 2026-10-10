from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional, cast
from uuid import UUID

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.publishing.pages.version_info import SitePageVersionInfo
from office365.sharepoint.publishing.user_info import UserInfo

if TYPE_CHECKING:
    from office365.sharepoint.publishing.pages.metadata_collection import (
        SitePageMetadataCollection,
    )


class SitePageMetadata(Entity):
    """Represents the core properties of a Site Page."""

    def __repr__(self):
        return self.file_name or self.absolute_url or self.entity_type_name

    @property
    def absolute_url(self) -> Optional[str]:
        """Gets the absolute Url of the Site Page."""
        return self.properties.get("AbsoluteUrl", None)

    @odata(name="AuthorByline")
    @property
    def author_byline(self) -> StringCollection:
        return self.properties.get("AuthorByline", StringCollection())

    @odata(name="CreatedBy")
    @property
    def created_by(self) -> UserInfo:
        """Specifies the user who created the page."""
        return self.properties.get("CreatedBy", UserInfo())

    @odata(name="LastModifiedBy")
    @property
    def last_modified_by(self) -> UserInfo:
        """Gets the user who last modified the current Site Page."""
        return self.properties.get("LastModifiedBy", UserInfo())

    @property
    def comments_disabled(self) -> Optional[bool]:
        """Indicates if comments are disabled for the current Site Page."""
        return self.properties.get("CommentsDisabled", None)

    @property
    def banner_image_url(self) -> Optional[str]:
        """Gets the banner image Url"""
        return self.properties.get("BannerImageUrl", None)

    @banner_image_url.setter
    def banner_image_url(self, value: str) -> None:
        """Sets the banner image Url"""
        self.set_property("BannerImageUrl", value)

    @property
    def content_type_id(self) -> Optional[str]:
        """Gets the content type ID of the current Site Page."""
        return self.properties.get("ContentTypeId", None)

    @content_type_id.setter
    def content_type_id(self, value: str) -> None:
        """Sets the content type ID of the current Site Page."""
        self.set_property("ContentTypeId", value)

    @property
    def description(self) -> Optional[str]:
        """Gets the description for the current Site Page"""
        return self.properties.get("Description", None)

    @property
    def does_user_have_edit_permission(self) -> Optional[bool]:
        """Indicates if the current user has edit permission to the Site Page."""
        return self.properties.get("DoesUserHaveEditPermission", None)

    @property
    def file_name(self) -> Optional[str]:
        """Gets the file name of the current Site Page."""
        return self.properties.get("FileName", None)

    @odata(name="FirstPublished")
    @property
    def first_published(self) -> Optional[datetime.datetime]:
        """Datetime of when the site page was initially published.
        The server MUST return Datetime.MinValue (00:00:00:0000000 UTC) when the site page has never been published.
        """
        return self.properties.get("FirstPublished", None)

    @property
    def is_page_checked_out_to_current_user(self) -> Optional[bool]:
        """Indicates if the Site Page is checked out to the current user."""
        return self.properties.get("IsPageCheckedOutToCurrentUser", None)

    @odata(name="VersionInfo")
    @property
    def version_info(self) -> SitePageVersionInfo:
        """Gets the version information for the most recently checked in version of the Site Page."""
        return self.properties.get("VersionInfo", SitePageVersionInfo())

    @property
    def parent_collection(self) -> SitePageMetadataCollection:
        from office365.sharepoint.publishing.pages.metadata_collection import (
            SitePageMetadataCollection,
        )

        return cast(SitePageMetadataCollection, self._parent_collection)

    @property
    def topic_header(self) -> Optional[str]:
        return self.properties.get("TopicHeader", None)

    @property
    def entity_type_name(self) -> str:
        return "SP.Publishing.SitePageMetadata"

    @property
    def asset_folder_id(self) -> Optional[int]:
        """Gets the AssetFolderId property"""
        return self.properties.get("AssetFolderId", None)

    @property
    def banner_thumbnail_url(self) -> Optional[str]:
        """Gets the BannerThumbnailUrl property"""
        return self.properties.get("BannerThumbnailUrl", None)

    @property
    def call_to_action(self) -> Optional[str]:
        """Gets the CallToAction property"""
        return self.properties.get("CallToAction", None)

    @property
    def categories(self) -> Optional[str]:
        """Gets the Categories property"""
        return self.properties.get("Categories", None)

    @property
    def comment_count(self) -> Optional[int]:
        """Gets the CommentCount property"""
        return self.properties.get("CommentCount", None)

    @property
    def created(self) -> Optional[datetime.datetime]:
        """Gets the Created property"""
        return self.properties.get("Created", datetime.datetime.min)

    @property
    def first_published_relative_time(self) -> Optional[str]:
        """Gets the FirstPublishedRelativeTime property"""
        return self.properties.get("FirstPublishedRelativeTime", None)

    @property
    def has_user_recently_modified(self) -> Optional[bool]:
        """Gets the HasUserRecentlyModified property"""
        return self.properties.get("HasUserRecentlyModified", None)

    @property
    def id(self) -> Optional[int]:
        """Gets the Id property"""
        return self.properties.get("Id", None)

    @property
    def is_web_welcome_page(self) -> Optional[bool]:
        """Gets the IsWebWelcomePage property"""
        return self.properties.get("IsWebWelcomePage", None)

    @property
    def like_count(self) -> Optional[int]:
        """Gets the LikeCount property"""
        return self.properties.get("LikeCount", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the ListId property"""
        return self.properties.get("ListId", None)

    @property
    def modified(self) -> Optional[datetime.datetime]:
        """Gets the Modified property"""
        return self.properties.get("Modified", datetime.datetime.min)

    @property
    def modified_relative_time(self) -> Optional[str]:
        """Gets the ModifiedRelativeTime property"""
        return self.properties.get("ModifiedRelativeTime", None)

    @property
    def page_layout_type(self) -> Optional[str]:
        """Gets the PageLayoutType property"""
        return self.properties.get("PageLayoutType", None)

    @property
    def path(self) -> ResourcePath:
        """Gets the Path property"""
        from office365.sharepoint.types.resource_path import ResourcePath

        return self.properties.get("Path", ResourcePath())

    @property
    def promoted_state(self) -> Optional[int]:
        """Gets the PromotedState property"""
        return self.properties.get("PromotedState", None)

    @property
    def publish_start_date(self) -> Optional[datetime.datetime]:
        """Gets the PublishStartDate property"""
        return self.properties.get("PublishStartDate", datetime.datetime.min)

    @property
    def social_bar_on_site_pages_disabled(self) -> Optional[bool]:
        """Gets the SocialBarOnSitePagesDisabled property"""
        return self.properties.get("SocialBarOnSitePagesDisabled", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def unique_id(self) -> Optional[UUID]:
        """Gets the UniqueId property"""
        return self.properties.get("UniqueId", None)

    @property
    def url(self) -> Optional[str]:
        """Gets the Url property"""
        return self.properties.get("Url", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the Version property"""
        return self.properties.get("Version", None)
