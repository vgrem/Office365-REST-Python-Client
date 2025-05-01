from office365.directory.applications.application import Application
from office365.directory.password_credential import PasswordCredential
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestApplication(GraphTestCase):
    target_app = None  # type: Application
    target_password = None  # type: PasswordCredential

    def test1_list_apps_and_templates(self):
        apps = self.client.applications.get().execute_query()
        self.assertIsNotNone(apps.resource_path)

        templates = self.client.application_templates.get().execute_query()
        self.assertIsNotNone(templates.resource_path)

    def test2_create_app(self):
        app_name = create_unique_name("App")
        new_app = self.client.applications.add(app_name).execute_query()
        self.assertIsNotNone(new_app.resource_path)
        self.__class__.target_app = new_app

    def test3_add_password(self):
        result = self.__class__.target_app.add_password("New password").execute_query()
        self.assertIsNotNone(result.value.secretText)
        self.__class__.target_password = result.value

    def test4_remove_password(self):
        self.__class__.target_app.remove_password(
            self.__class__.target_password.keyId
        ).execute_query()

    def test5_delete_app(self):
        app_to_del = self.__class__.target_app
        app_to_del.delete_object(True).execute_query()
