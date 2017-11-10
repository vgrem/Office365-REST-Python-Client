from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests.sharepoint_case import SPTestCase
from tests.test_utilities import ListExtensions


class TestListItem(SPTestCase):
    target_list = None

    @classmethod
    def setUpClass(cls):
        super(TestListItem, cls).setUpClass()

    def setUp(self):
        self.target_list = ListExtensions.ensure_list(self.context.web,
                                                      ListCreationInformation("Tasks",
                                                                              None,
                                                                              ListTemplateType.Tasks)
                                                      )

    def test_1_create_list_item(self):
        item_properties = {'Title': 'Task 1978', '__metadata': {'type': 'SP.Data.TasksListItem'}}
        item = self.target_list.add_item(item_properties)
        self.context.execute_query()
        self.assertIsNotNone(item.properties["Title"])

