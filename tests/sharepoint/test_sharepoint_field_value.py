from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.fields.field_creation_information import FieldCreationInformation
from office365.sharepoint.fields.field_type import FieldType
from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue
from office365.sharepoint.fields.fieldMultiChoice import FieldMultiChoice
from office365.sharepoint.fields.fieldMultiChoiceValue import FieldMultiChoiceValue
from office365.sharepoint.fields.fieldMultiLookupValue import FieldMultiLookupValue
from office365.sharepoint.fields.fieldMultiUserValue import FieldMultiUserValue
from office365.sharepoint.fields.fieldUserValue import FieldUserValue
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestFieldValue(SPTestCase):
    target_list = None  # type: List
    target_item = None  # type: ListItem
    target_field = None  # type: FieldMultiChoice

    @classmethod
    def setUpClass(cls):
        super(TestFieldValue, cls).setUpClass()
        cls.target_list = cls.ensure_list(cls.client.web,
                                          ListCreationInformation(
                                              "Tasks N%s" % random_seed,
                                              None,
                                              ListTemplateType.TasksWithTimelineAndHierarchy))

    @classmethod
    def tearDownClass(cls):
        cls.target_list.delete_object()
        cls.client.execute_query()

    def test_1_set_field_text_value(self):
        items = self.target_list.items
        create_info = {
            "Title": "Task1",
        }
        self.__class__.target_item = self.target_list.add_item(create_info)
        self.client.load(items)
        self.client.execute_query()
        self.assertGreaterEqual(len(items), 1)

    def test_2_set_field_multi_lookup_value(self):
        lookup_id = self.__class__.target_item.properties['Id']

        items = self.target_list.items
        create_info = {
            "Title": "Task2"
        }
        multi_lookup_value = FieldMultiLookupValue()
        multi_lookup_value.add(FieldLookupValue(lookup_id))
        new_item = self.target_list.add_item(create_info)
        new_item.set_property("Predecessors", multi_lookup_value)
        self.client.load(items)
        self.client.execute_query()
        self.assertGreaterEqual(len(items), 1)

    def test_3_set_field_multi_user_value(self):
        current_user = self.client.web.currentUser
        multi_user_value = FieldMultiUserValue()
        multi_user_value.add(FieldUserValue.from_user(current_user))

        item_to_update = self.__class__.target_item
        item_to_update.set_property("AssignedTo",  multi_user_value)
        item_to_update.update()
        self.client.execute_query()

    def test_4_create_list_field(self):
        field_name = "TaskStatuses"
        create_field_info = FieldCreationInformation(field_name, FieldType.MultiChoice)
        [create_field_info.Choices.add(choice) for choice in ["Not Started", "In Progress", "Completed", "Deferred"]]
        created_field = self.__class__.target_list.fields.add(create_field_info)
        self.client.execute_query()
        self.assertIsInstance(created_field, FieldMultiChoice)
        self.__class__.target_field = created_field

    def test_5_set_field_multi_choice_value(self):
        item_to_update = self.__class__.target_item
        multi_choice_value = FieldMultiChoiceValue(["In Progress"])
        item_to_update.set_property("TaskStatuses", multi_choice_value)
        item_to_update.update()
        self.client.execute_query()
