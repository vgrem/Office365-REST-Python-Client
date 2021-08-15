from office365.onenote.entity_base_model import OnenoteEntityBaseModel


class OnenoteResource(OnenoteEntityBaseModel):
    """An image or other file resource on a OneNote page."""

    @property
    def content_url(self):
        """The URL for downloading the content

        :rtype: str or None
        """
        return self.properties.get("contentUrl", None)
