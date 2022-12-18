from office365.directory.applications.service_principal import ServicePrincipal
from tests import test_tenant
from tests.graph_case import GraphTestCase


class TestServicePrincipal(GraphTestCase):
    target_object = None  # type: ServicePrincipal

    def test1_create_service_principal(self):
        #apps = self.client.applications.get().filter("publisherDomain eq '{0}'".format(test_tenant)).top(1).execute_query()
        #self.assertEqual(len(apps), 1)
        #service_principal = self.client.service_principals.add(appId=apps[0].app_id).execute_query()
        #self.assertIsNotNone(service_principal.resource_path)
        #self.__class__.target_object = service_principal
        pass

    def test2_list_service_principals(self):
        principals = self.client.service_principals.get().execute_query()
        self.assertIsNotNone(principals.resource_path)

    def test3_delete_service_principal(self):
        #self.__class__.target_object.delete_object().execute_query()
        pass
