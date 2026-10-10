from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.entity import Entity
from office365.sharepoint.sharing.principal import Principal


class SharedDocumentInfo(Entity):
    """"""

    @property
    def activity(self) -> Optional[str]:
        """"""
        return self.properties.get("Activity", None)

    @property
    def author(self):
        """"""
        return self.properties.get("Author", Principal())

    @property
    def caller_stack(self) -> Optional[str]:
        """"""
        return self.properties.get("CallerStack", None)

    @property
    def color_hex(self) -> Optional[str]:
        """"""
        return self.properties.get("ColorHex", None)

    @property
    def color_tag(self) -> Optional[str]:
        """"""
        return self.properties.get("ColorTag", None)

    @property
    def content_type_id(self) -> Optional[str]:
        """"""
        return self.properties.get("ContentTypeId", ContentTypeId())

    @property
    def entity_type_name(self):
        return "SP.Sharing.SharedDocumentInfo"

    @property
    def drive_access_token(self) -> Optional[str]:
        """Gets the DriveAccessToken property"""
        return self.properties.get("DriveAccessToken", None)

    @property
    def drive_access_token_v21(self) -> Optional[str]:
        """Gets the DriveAccessTokenV21 property"""
        return self.properties.get("DriveAccessTokenV21", None)

    @property
    def drive_url(self) -> Optional[str]:
        """Gets the DriveUrl property"""
        return self.properties.get("DriveUrl", None)

    @property
    def editor(self) -> Principal:
        """Gets the Editor property"""
        from office365.sharepoint.sharing.principal import Principal

        return self.properties.get("Editor", Principal())

    @property
    def emoji(self) -> Optional[str]:
        """Gets the Emoji property"""
        return self.properties.get("Emoji", None)

    @property
    def extension(self) -> Optional[str]:
        """Gets the Extension property"""
        return self.properties.get("Extension", None)

    @property
    def file_leaf_ref(self) -> Optional[str]:
        """Gets the FileLeafRef property"""
        return self.properties.get("FileLeafRef", None)

    @property
    def file_ref(self) -> Optional[str]:
        """Gets the FileRef property"""
        return self.properties.get("FileRef", None)

    @property
    def is_container(self) -> Optional[bool]:
        """Gets the IsContainer property"""
        return self.properties.get("IsContainer", None)

    @property
    def linking_url(self) -> Optional[str]:
        """Gets the LinkingUrl property"""
        return self.properties.get("LinkingUrl", None)

    @property
    def list_id(self) -> Optional[UUID]:
        """Gets the ListId property"""
        return self.properties.get("ListId", None)

    @property
    def list_item_id(self) -> Optional[int]:
        """Gets the ListItemId property"""
        return self.properties.get("ListItemId", None)

    @property
    def media_base_url(self) -> Optional[str]:
        """Gets the MediaBaseUrl property"""
        return self.properties.get("MediaBaseUrl", None)

    @property
    def modified(self) -> Optional[datetime]:
        """Gets the Modified property"""
        return self.properties.get("Modified", datetime.min)

    @property
    def office_bundle_generate(self) -> Optional[str]:
        """Gets the OfficeBundleGenerate property"""
        return self.properties.get("OfficeBundleGenerate", None)

    @property
    def office_bundle_get_fragment(self) -> Optional[str]:
        """Gets the OfficeBundleGetFragment property"""
        return self.properties.get("OfficeBundleGetFragment", None)

    @property
    def pdf_conversion_url(self) -> Optional[str]:
        """Gets the PdfConversionUrl property"""
        return self.properties.get("PdfConversionUrl", None)

    @property
    def prog_id(self) -> Optional[str]:
        """Gets the ProgId property"""
        return self.properties.get("ProgId", None)

    @property
    def server_redirected_embed_url(self) -> Optional[str]:
        """Gets the ServerRedirectedEmbedUrl property"""
        return self.properties.get("ServerRedirectedEmbedUrl", None)

    @property
    def server_redirected_preview_url(self) -> Optional[str]:
        """Gets the ServerRedirectedPreviewUrl property"""
        return self.properties.get("ServerRedirectedPreviewUrl", None)

    @property
    def server_redirected_url(self) -> Optional[str]:
        """Gets the ServerRedirectedUrl property"""
        return self.properties.get("ServerRedirectedUrl", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def site_url(self) -> Optional[str]:
        """Gets the SiteUrl property"""
        return self.properties.get("SiteUrl", None)

    @property
    def sp_item_url(self) -> Optional[str]:
        """Gets the SpItemUrl property"""
        return self.properties.get("SpItemUrl", None)

    @property
    def sp_resource_url(self) -> Optional[str]:
        """Gets the SpResourceUrl property"""
        return self.properties.get("SpResourceUrl", None)

    @property
    def thumbnail_url(self) -> Optional[str]:
        """Gets the ThumbnailUrl property"""
        return self.properties.get("ThumbnailUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def unique_id(self) -> Optional[UUID]:
        """Gets the UniqueId property"""
        return self.properties.get("UniqueId", None)

    @property
    def url_path(self) -> Optional[str]:
        """Gets the UrlPath property"""
        return self.properties.get("UrlPath", None)

    @property
    def video_manifest_url(self) -> Optional[str]:
        """Gets the VideoManifestUrl property"""
        return self.properties.get("VideoManifestUrl", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebId property"""
        return self.properties.get("WebId", None)
