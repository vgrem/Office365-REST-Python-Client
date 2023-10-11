from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestServicePrincipal(GraphTestCase):
    target_object = None  # type: ServicePrincipal
    target_app = None  # type: Application
    password_creds = None  # type: PasswordCredential

    @classmethod
    def setUpClass(cls):
        super(TestServicePrincipal, cls).setUpClass()
        app_name = create_unique_name("App")
        cls.target_app = cls.client.applications.add(
            displayName=app_name
        ).execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_app.delete_object(True).execute_query()

    def test1_create_service_principal(self):
        service_principal = self.client.service_principals.add(
            self.target_app.app_id
        ).execute_query()
        self.assertIsNotNone(service_principal.resource_path)
        self.__class__.target_object = service_principal

    def test2_list_service_principals(self):
        principals = self.client.service_principals.get().execute_query()
        self.assertIsNotNone(principals.resource_path)

    def test3_get_by_app_id(self):
        principal = (
            self.client.service_principals.get_by_app_id(self.target_app.app_id)
            .get()
            .execute_query()
        )
        self.assertIsNotNone(principal.resource_path)

    def test4_add_password(self):
        result = self.__class__.target_object.add_password(
            "Password friendly name"
        ).execute_query()
        self.assertIsNotNone(result.value)
        self.__class__.password_creds = result.value

    def test5_remove_password(self):
        key_id = self.__class__.password_creds.keyId
        self.__class__.target_object.remove_password(key_id).execute_query()

    def test6_delete_service_principal(self):
        self.__class__.target_object.delete_object().execute_query()

    def test7_list_deleted(self):
        result = (
            self.__class__.client.directory.deleted_service_principals.get().execute_query()
        )
        self.assertIsNotNone(result.resource_path)
        self.assertGreater(len(result), 0)
