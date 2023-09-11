from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class PhotosMigration(BaseEntity):

    def __init__(self, context):
        static_path = ResourcePath("Microsoft.SharePoint.Photos.PhotosMigration")
        super(PhotosMigration, self).__init__(context, static_path)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Photos.PhotosMigration"
