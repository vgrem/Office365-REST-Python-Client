from office365.sharepoint.fields.choice import FieldChoice
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.geolocation_value import FieldGeolocationValue
from office365.sharepoint.fields.lookup_value import FieldLookupValue
from office365.sharepoint.fields.multi_choice import FieldMultiChoice
from office365.sharepoint.fields.multi_choice_value import FieldMultiChoiceValue
from office365.sharepoint.fields.multi_lookup_value import FieldMultiLookupValue
from office365.sharepoint.fields.multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.fields.url_value import FieldUrlValue
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType
from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestFieldValue(SPTestCase):
    target_list = None  # type: List
    target_item = None  # type: ListItem
    target_field = None  # type: FieldMultiChoice

    @classmethod
    def setUpClass(cls):
        super(TestFieldValue, cls).setUpClass()
        cls.multi_lookup_field_name = "PredecessorsAlt"
        cls.url_field_name = "DocumentationLink"
        cls.geo_field_name = "Place"
        cls.choice_field_name = "TaskStatus"
        cls.multi_choice_field_name = "TaskStatuses"
        cls.user_field_name = "PrimaryApprover"
        cls.lookup_field_name = "RelatedDocuments"
        cls.target_list = cls.ensure_list(
            cls.client.web,
            ListCreationInformation(
                create_unique_name("Tasks N"),
                None,
                ListTemplateType.TasksWithTimelineAndHierarchy,
            ),
        )
        cls.lookup_list = (
            cls.client.web.default_document_library().get().execute_query()
        )

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object().execute_query()

    def test1_get_web_available_fields(self):
        web_fields = self.client.web.available_fields.get().execute_query()
        self.assertIsNotNone(web_fields.resource_path)

    def test2_set_field_text_value(self):
        items = self.target_list.items
        create_info = {
            "Title": "Task1",
        }
        self.__class__.target_item = self.target_list.add_item(
            create_info
        ).execute_query()
        self.client.load(items)
        self.client.execute_query()
        self.assertGreaterEqual(len(items), 1)

    def test3_create_multi_lookup_field(self):
        lookup_field = self.target_list.fields.add_lookup_field(
            title=self.multi_lookup_field_name,
            lookup_list=self.target_list.properties["Id"],
            lookup_field_name="Title",
            allow_multiple_values=True,
        ).execute_query()
        self.assertEqual(lookup_field.type_as_string, "LookupMulti")

    def test4_set_field_multi_lookup_value(self):
        item_to_update = self.__class__.target_list.get_item_by_id(
            self.__class__.target_item.id
        )
        lookup_id = self.__class__.target_item.id
        field_value = FieldMultiLookupValue()
        field_value.add(FieldLookupValue(lookup_id))
        updated = (
            item_to_update.set_property(self.multi_lookup_field_name, field_value)
            .update()
            .get()
            .execute_query()
        )
        self.assertIsInstance(
            updated.properties[self.multi_lookup_field_name], FieldMultiLookupValue
        )

    def test5_set_field_multi_user_value(self):
        current_user = self.client.web.current_user
        multi_user_value = FieldMultiUserValue()
        multi_user_value.add(FieldUserValue.from_user(current_user))
        item_to_update = self.__class__.target_item
        item_to_update.set_property(
            "AssignedTo", multi_user_value
        ).update().execute_query()

    def test6_create_list_multi_choice_field(self):
        choices = ["Not Started", "In Progress", "Completed", "Deferred"]
        created_field = self.target_list.fields.add_choice_field(
            title=self.multi_choice_field_name, values=choices, multiple_values=True
        ).execute_query()
        self.assertIsInstance(created_field, FieldMultiChoice)
        self.__class__.target_field = created_field

    def test7_set_field_multi_choice_value(self):
        item_to_update = self.__class__.target_item
        multi_choice_value = FieldMultiChoiceValue(["In Progress"])
        item_to_update.set_property(self.multi_choice_field_name, multi_choice_value)
        item_to_update.update().execute_query()

    def test8_create_list_choice_field(self):
        choices = ["Not Started", "In Progress", "Completed", "Deferred"]
        created_field = self.target_list.fields.add_choice_field(
            title=self.choice_field_name, values=choices
        ).execute_query()
        self.assertIsInstance(created_field, FieldChoice)

    def test9_set_field_choice_value(self):
        item_to_update = self.__class__.target_item
        choice_value = "In Progress"
        item_to_update.set_property(self.choice_field_name, choice_value)
        item_to_update.update().execute_query()

    def test_10_get_lookup_field_choices(self):
        result = self.target_list.get_lookup_field_choices(
            self.multi_choice_field_name
        ).execute_query()
        self.assertIsNotNone(result.value)

    def test_11_create_list_url_field(self):
        url_field = self.target_list.fields.add_url_field(
            self.url_field_name
        ).execute_query()
        self.assertIsNotNone(url_field.resource_path)
        self.assertEqual(url_field.type_as_string, "URL")

    def test_12_set_url_field_value(self):
        item_to_update = self.__class__.target_item
        url = "https://docs.microsoft.com/en-us/previous-versions/office/sharepoint-server/ms472498(v=office.15)"
        field_value = FieldUrlValue(url)
        updated = (
            item_to_update.set_property(self.url_field_name, field_value)
            .update()
            .get()
            .execute_query()
        )
        self.assertIsNotNone(updated.properties.get(self.url_field_name))
        # self.assertIsInstance(updated.properties.get('DocumentationLink'), FieldUrlValue)

    def test_13_create_list_geolocation_field(self):
        geo_field = self.target_list.fields.add_geolocation_field(
            self.geo_field_name
        ).execute_query()
        self.assertIsNotNone(geo_field.resource_path)
        self.assertEqual(geo_field.type_as_string, "Geolocation")
        # self.assertIsInstance(geo_field, FieldGeolocation)

    def test_14_set_geo_field_value(self):
        item_to_update = self.__class__.target_item
        field_value = FieldGeolocationValue(59.940117, 29.8145056)
        updated = (
            item_to_update.set_property(self.geo_field_name, field_value)
            .update()
            .get()
            .execute_query()
        )
        self.assertIsNotNone(updated.properties.get(self.geo_field_name))

    def test_15_create_list_user_field(self):
        create_field_info = FieldCreationInformation(
            self.user_field_name, FieldType.User
        )
        user_field = self.target_list.fields.add(create_field_info).execute_query()
        self.assertIsNotNone(user_field.resource_path)
        self.assertEqual(user_field.type_as_string, "User")

    def test_16_set_user_field_value(self):
        item_to_update = self.__class__.target_item
        current_user = self.client.web.current_user
        user_value = FieldUserValue.from_user(current_user)
        updated = (
            item_to_update.set_property(self.user_field_name, user_value)
            .update()
            .get()
            .execute_query()
        )
        self.assertIsNotNone(updated.properties.get(self.user_field_name))

    def test_17_create_list_lookup_field(self):
        lookup_field = self.target_list.fields.add_lookup_field(
            title=self.lookup_field_name,
            lookup_list=self.lookup_list.properties["Id"],
            lookup_field_name="Title",
        ).execute_query()
        self.assertEqual(lookup_field.type_as_string, "Lookup")

    def test_18_set_lookup_field_value(self):
        item_to_update = self.__class__.target_item
        lookup_items = (
            self.client.web.default_document_library().get_items().execute_query()
        )
        if len(lookup_items) > 0:
            lookup_value = FieldLookupValue(lookup_id=lookup_items[0].properties["Id"])
            updated = (
                item_to_update.set_property(self.lookup_field_name, lookup_value)
                .update()
                .get()
                .execute_query()
            )
            self.assertIsNotNone(updated.properties.get(self.lookup_field_name))
