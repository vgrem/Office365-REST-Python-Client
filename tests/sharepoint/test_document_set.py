from tests import random_seed
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
                                             "Archive Documents N%s" % random_seed,
                                             None,
                                             ListTemplateType.DocumentLibrary))

    @classmethod
    def tearDownClass(cls):
        cls.target_lib.delete_object().execute_query()

    def test1_create_document_set(self):
        name = "DocSet"
        doc_set = DocumentSet.create(self.client, self.target_lib.rootFolder, name)
        self.client.execute_query()
        self.assertEqual(doc_set.properties["Name"], name)
