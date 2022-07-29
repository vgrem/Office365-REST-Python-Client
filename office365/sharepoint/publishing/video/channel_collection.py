from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.video.channel import VideoChannel


class VideoChannelCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(VideoChannelCollection, self).__init__(context, VideoChannel, resource_path)
