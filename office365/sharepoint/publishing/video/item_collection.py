from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.video.item import VideoItem


class VideoItemCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(VideoItemCollection, self).__init__(context, VideoItem, resource_path)
