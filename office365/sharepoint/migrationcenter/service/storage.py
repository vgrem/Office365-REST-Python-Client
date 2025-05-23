from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity


class MigrationCenterStorage(Entity):
    """ """

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath(
                "Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationCenterStorage"
            )
        super(MigrationCenterStorage, self).__init__(context, resource_path)
