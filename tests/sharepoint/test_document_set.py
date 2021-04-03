from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.documentmanagement.document_set import DocumentSet
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


class TestSharePointDocumentSet(SPTestCase):
    target_lib = None  # type: List

    @classmethod
    def setUpClass(cls):
        super(TestSharePointDocumentSet, cls).setUpClass()
        cls.target_lib = cls.ensure_list(cls.client.web,
                                         ListCreationInformation(
                                             create_unique_name("Archive Documents"),
                                             None,
                                             ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_lib.delete_object().execute_query()

    def test1_create_document_set(self):
        name = "DocSet"
        doc_set = DocumentSet.create(self.client, self.target_lib.root_folder, name)
        self.client.execute_query()
        self.assertEqual(doc_set.properties["Name"], name)
