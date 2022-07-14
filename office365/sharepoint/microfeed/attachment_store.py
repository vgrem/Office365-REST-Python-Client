from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class MicrofeedAttachmentStore(BaseEntity):

    def __init__(self, context):
        super(MicrofeedAttachmentStore, self).__init__(context, ResourcePath("SP.Microfeed.MicrofeedAttachmentStore"))
