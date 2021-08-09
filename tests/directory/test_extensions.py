from office365.directory.applications.application import Application
from office365.directory.extensions.extension_property import ExtensionProperty
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestExtensions(GraphTestCase):
    target_app = None  # type: Application
    target_extension = None  # type: ExtensionProperty

    @classmethod
    def setUpClass(cls):
        super(TestExtensions, cls).setUpClass()
        app_name = create_unique_name("App")
        cls.target_app = cls.client.applications.add(displayName=app_name).execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_app.delete_object(True).execute_query()

    def test1_list_extensions(self):
        extensions = self.client.directory_objects.get_available_extension_properties().execute_query()
        self.assertIsNotNone(extensions.resource_path)

    def test2_create_extension(self):
        new_extension = self.__class__.target_app.extension_properties.add(name="extensionName")
        self.client.execute_query()
        self.assertIsNotNone(new_extension.resource_path)
        self.__class__.target_extension = new_extension

    def test3_delete_extension(self):
        self.__class__.target_extension.delete_object().execute_query()
