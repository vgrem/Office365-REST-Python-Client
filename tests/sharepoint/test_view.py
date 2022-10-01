import uuid

from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.views.field_collection import ViewFieldCollection
from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType
from office365.sharepoint.views.view import View
from office365.sharepoint.views.create_information import ViewCreationInformation


class TestSPView(SPTestCase):
    target_list = None  # type: List
    target_view = None  # type: View
    target_field = None  # type: Field
    view_fields_count = None

    @classmethod
    def setUpClass(cls):
        super(TestSPView, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation("Tasks",
                                                                  None,
                                                                  ListTemplateType.Tasks)
                                          )

        field_info = FieldCreationInformation("TaskComment_" + uuid.uuid4().hex, FieldType.Note)
        cls.target_field = cls.target_list.fields.add(field_info).execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object().execute_query()

    def test1_get_all_views(self):
        all_views = self.target_list.views.get().execute_query()
        self.assertGreater(len(all_views), 1)

    def test2_create_view(self):
        view_properties = ViewCreationInformation()
        view_properties.Title = create_unique_name("My Tasks")
        view_properties.PersonalView = True
        view_properties.Query = "<Where><Eq><FieldRef ID='AssignedTo' /><Value " \
                                "Type='Integer'><UserID/></Value></Eq></Where> "

        new_view = self.target_list.views.add(view_properties).execute_query()
        self.assertEqual(view_properties.Title, new_view.properties['Title'])
        self.__class__.target_view = new_view

    def test3_read_view(self):
        view_to_read = self.__class__.target_view.get().execute_query()
        self.assertIsNotNone(view_to_read.resource_path)

    def test4_render_as_html(self):
        result = self.__class__.target_view.render_as_html().execute_query()
        self.assertIsNotNone(result.value)

    def test5_get_default_view_items(self):
        view_items = self.target_list.default_view.get_items().get().execute_query()
        self.assertIsNotNone(view_items.resource_path)

    def test6_get_view_items(self):
        view_items = self.__class__.target_view.get_items().get().execute_query()
        self.assertIsNotNone(view_items.resource_path)

    def test7_update_view(self):
        title_updated = self.__class__.target_view.properties["Title"] + "_updated"
        view_to_update = self.__class__.target_view
        view_to_update.set_property('Title', title_updated).update().execute_query()

        result = self.target_list.views.filter("Title eq '{0}'".format(title_updated)).get().execute_query()
        self.assertEqual(len(result), 1)

    def test8_get_view_fields(self):
        view = self.__class__.target_view.expand(["ViewFields"]).get().execute_query()
        self.assertIsNotNone(view.view_fields)
        self.assertIsInstance(view.view_fields, ViewFieldCollection)
        self.__class__.view_fields_count = len(view.view_fields)

    def test9_add_view_field(self):
        field_name = self.__class__.target_field.internal_name
        self.__class__.target_view.view_fields.add_view_field(field_name).execute_query()
        after_view_fields = self.__class__.target_view.view_fields.get().execute_query()
        self.assertEqual(self.__class__.view_fields_count + 1, len(after_view_fields))

    def test_10_move_view_field_to(self):
        field_name = self.__class__.target_field.internal_name
        self.__class__.target_view.view_fields.move_view_field_to(field_name, 2).execute_query()
        after_view_fields = self.__class__.target_view.view_fields.get().execute_query()
        self.assertEqual(after_view_fields[2], field_name)

    def test_11_remove_view_field(self):
        field_name = self.__class__.target_field.internal_name
        self.__class__.target_view.view_fields.remove_view_field(field_name).execute_query()
        after_view_fields = self.__class__.target_view.view_fields.get().execute_query()
        self.assertEqual(self.__class__.view_fields_count, len(after_view_fields))

    def test_12_remove_all_view_fields(self):
        self.__class__.target_view.view_fields.remove_all_view_fields().execute_query()
        after_view_fields = self.__class__.target_view.view_fields.get().execute_query()
        self.assertEqual(0, len(after_view_fields))

    def test_13_get_view_changes(self):
        changes = self.client.site.get_changes(ChangeQuery(view=True)).execute_query()
        self.assertGreater(len(changes), 0)

    def test_14_delete_view(self):
        view_to_delete = self.__class__.target_view
        view_to_delete.delete_object().execute_query()
