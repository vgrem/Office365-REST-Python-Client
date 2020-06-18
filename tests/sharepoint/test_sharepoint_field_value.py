from office365.sharepoint.list import List
from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType
from tests import random_seed
from tests.sharepoint.sharepoint_case import SPTestCase


class TestFieldValue(SPTestCase):
    target_list = None  # type: List

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

    def test_1_get_field_user_value(self):
        pass
