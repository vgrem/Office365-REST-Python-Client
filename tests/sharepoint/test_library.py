from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPLibrary(SPTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSPLibrary, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_default_library(self):
        default_lib = self.client.web.default_document_library().get().execute_query()
        self.assertIsNotNone(default_lib.id)

    # def test2_reset_doc_id(self):
    #    lib = self.client.web.default_document_library()
    #    lib.reset_doc_id().execute_query()
    #    #self.assertIsNotNone(default_lib.id)
