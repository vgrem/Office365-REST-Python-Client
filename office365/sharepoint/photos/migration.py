from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class PhotosMigration(Entity):
    def __init__(self, context):
        static_path = ResourcePath("Microsoft.SharePoint.Photos.PhotosMigration")
        super(PhotosMigration, self).__init__(context, static_path)

    def migrate_photos_data(self):
        """ """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "MigratePhotosData", None, None, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Photos.PhotosMigration"
