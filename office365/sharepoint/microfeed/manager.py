from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class MicrofeedManager(BaseEntity):

    def __init__(self, context):
        super(MicrofeedManager, self).__init__(context, ResourcePath("SP.Microfeed.MicrofeedManager"))
