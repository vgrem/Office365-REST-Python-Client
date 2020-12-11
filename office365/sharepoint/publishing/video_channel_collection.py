from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.publishing.video_channel import VideoChannel


class VideoChannelCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(VideoChannelCollection, self).__init__(context, VideoChannel, resource_path)
