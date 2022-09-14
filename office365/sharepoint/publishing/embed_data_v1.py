from office365.sharepoint.base_entity import BaseEntity


class EmbedDataV1(BaseEntity):
    """Represents embedded meta data of the page."""

    def url(self):
        """
        The URL of the page.

        :rtype: str
        """
        return self.properties.get("Url", None)

    def video_id(self):
        """
        If the page represents a video, the value will be video id.

        :rtype: str
        """
        return self.properties.get("VideoId", None)

    def web_id(self):
        """
        If the page belongs to website, the value will be website id, otherwise the value will be empty.

        :rtype: str
        """
        return self.properties.get("WebId", None)
