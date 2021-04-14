from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.publishing.video_item import VideoItem


class VideoItemCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(VideoItemCollection, self).__init__(context, VideoItem, resource_path)
