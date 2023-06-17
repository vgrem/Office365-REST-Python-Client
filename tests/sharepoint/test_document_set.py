from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.documentmanagement.document_set import DocumentSet
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType


class TestSharePointDocumentSet(SPTestCase):
    target_lib = None  # type: List
    target_doc_set = None  # type: DocumentSet

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
        doc_set_title = create_unique_name("DocSet N")
        doc_set = DocumentSet.create(self.client, self.target_lib.root_folder, doc_set_title).execute_query()
        self.assertEqual(doc_set.name, doc_set_title)
        self.assertIsNotNone(doc_set.resource_path)
        self.__class__.target_doc_set = doc_set

    def test2_delete_document_set(self):
        self.__class__.target_doc_set.delete_object().execute_query()
