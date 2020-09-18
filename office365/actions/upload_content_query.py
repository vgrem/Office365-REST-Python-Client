from office365.resource_path_url import ResourcePathUrl
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class UploadContentQuery(ServiceOperationQuery):
    def __init__(self, parent_entity, name, content):
        from office365.onedrive.driveItem import DriveItem
        return_type = DriveItem(parent_entity.context, ResourcePathUrl(name, parent_entity.resource_path))
        super(UploadContentQuery, self).__init__(return_type, "content", None, content, None, return_type)
