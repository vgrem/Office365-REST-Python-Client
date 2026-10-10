from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class EmbedDataV1(Entity):
    """Represents embedded meta data of the page."""

    def url(self) -> Optional[str]:
        """The URL of the page."""
        return self.properties.get("Url", None)

    def video_id(self) -> Optional[str]:
        """If the page represents a video, the value will be video id."""
        return self.properties.get("VideoId", None)

    def web_id(self) -> Optional[str]:
        """If the page belongs to website, the value will be website id, otherwise the value will be empty."""
        return self.properties.get("WebId", None)

    @property
    def allow_https_embed(self) -> Optional[bool]:
        """Gets the AllowHttpsEmbed property"""
        return self.properties.get("AllowHttpsEmbed", None)

    @property
    def creator_name(self) -> Optional[str]:
        """Gets the CreatorName property"""
        return self.properties.get("CreatorName", None)

    @property
    def date_published_at(self) -> Optional[str]:
        """Gets the DatePublishedAt property"""
        return self.properties.get("DatePublishedAt", None)

    @property
    def decoded_url(self) -> Optional[str]:
        """Gets the DecodedUrl property"""
        return self.properties.get("DecodedUrl", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def duration_in_seconds(self) -> Optional[int]:
        """Gets the DurationInSeconds property"""
        return self.properties.get("DurationInSeconds", None)

    @property
    def embed_service_response_code(self) -> Optional[int]:
        """Gets the EmbedServiceResponseCode property"""
        return self.properties.get("EmbedServiceResponseCode", None)

    @property
    def error_message(self) -> Optional[str]:
        """Gets the ErrorMessage property"""
        return self.properties.get("ErrorMessage", None)

    @property
    def html(self) -> Optional[str]:
        """Gets the Html property"""
        return self.properties.get("Html", None)

    @property
    def list_id(self) -> Optional[str]:
        """Gets the ListId property"""
        return self.properties.get("ListId", None)

    @property
    def publisher_name(self) -> Optional[str]:
        """Gets the PublisherName property"""
        return self.properties.get("PublisherName", None)

    @property
    def response_code(self) -> Optional[int]:
        """Gets the ResponseCode property"""
        return self.properties.get("ResponseCode", None)

    @property
    def site_id(self) -> Optional[str]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def thumbnail_url(self) -> Optional[str]:
        """Gets the ThumbnailUrl property"""
        return self.properties.get("ThumbnailUrl", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def type_(self) -> Optional[str]:
        """Gets the Type property"""
        return self.properties.get("Type", None)

    @property
    def unique_id(self) -> Optional[str]:
        """Gets the UniqueId property"""
        return self.properties.get("UniqueId", None)

    @property
    def entity_type_name(self):
        return "SP.Publishing.EmbedDataV1"

    @property
    def type(self) -> Optional[str]:
        """Gets the Type property"""
        return self.properties.get("Type", None)
