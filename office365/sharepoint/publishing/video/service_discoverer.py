from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class VideoServiceDiscoverer(BaseEntity):

    def __init__(self, context):
        super(VideoServiceDiscoverer, self).__init__(context, ResourcePath("SP.Publishing.VideoServiceDiscoverer"))

    @property
    def video_portal_url(self):
        """
        :rtype: str or None
        """
        return self.properties.get("VideoPortalUrl", None)
