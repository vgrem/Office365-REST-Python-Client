from office365.sharepoint.sites.azure_container_Info import (
    ProvisionedTemporaryAzureContainerInfo,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestMigration(SPTestCase):

    azure_container_info = None  # type: ProvisionedTemporaryAzureContainerInfo

    def test1_provision_temporary_azure_container(self):
        result = self.client.site.provision_temporary_azure_container().execute_query()
        self.assertTrue(result.value)
        self.__class__.azure_container_info = result.value

    # def test2_create_migration_job(self):
    #    web = self.client.web.get().execute_query()
    #    result = self.client.site.create_migration_job(
    #        g_web_id=web.id,
    #        azure_container_source_uri=self.__class__.azure_container_info.Uri
    #    ).execute_query()
    #    self.assertIsNotNone(result.value)

    def test4_get_migration_center_storage(self):
        from office365.sharepoint.migrationcenter.service.storage import (
            MigrationCenterStorage,
        )

        result = MigrationCenterStorage(self.client).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test5_get_migration_performance_data(self):
    #    from office365.sharepoint.migrationcenter.service.services import MigrationCenterServices
    #    result = MigrationCenterServices(self.client).performance_data.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test6_get_copy_job_progress(self):
        result = self.client.site.get_copy_job_progress().execute_query()
        self.assertIsNotNone(result.value)
