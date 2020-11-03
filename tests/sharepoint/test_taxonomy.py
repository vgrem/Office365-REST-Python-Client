import uuid

from office365.sharepoint.fields.field import Field
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPTaxonomy(SPTestCase):

    target_field = None   # type: Field

    @classmethod
    def setUpClass(cls):
        super(TestSPTaxonomy, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_taxonomy_field(self):
        ssp_id = "f02be691-d551-462f-aaae-e1c89168cd0b"
        term_set_id = "b49f64b3-4722-4336-9a5c-56c326b344d4"
        text_field_id = "cd790052-00e3-4317-a090-365cd85795b6"
        # list_id = "b9b8e2ef-6f9a-400b-a218-6a4899ea0121"
        # web_id = "cd5c86f3-261c-4d3a-8a91-34d6392cdfb9"
        tax_field = self.client.web.default_document_library().fields\
            .create_taxonomy_field(name="Category",
                                   ssp_id=ssp_id,
                                   term_set_id=term_set_id,
                                   text_field_id=text_field_id).execute_query()
        self.assertIsNotNone(tax_field.resource_path)
        self.__class__.target_field = tax_field

    def test2_delete_taxonomy_field(self):
        self.__class__.target_field.delete_object().execute_query()
