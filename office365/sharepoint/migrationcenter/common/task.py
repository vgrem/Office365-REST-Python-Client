from office365.sharepoint.migrationcenter.common.task_entity_data import MigrationTaskEntityData


class MigrationTask(MigrationTaskEntityData):

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationTask"
