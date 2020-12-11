from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class VideoServiceManager(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("SP.Publishing.VideoServiceManager"))
