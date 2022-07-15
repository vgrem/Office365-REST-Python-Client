from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.field import Field
from office365.sharepoint.taxonomy.field import TaxonomyField
from office365.sharepoint.taxonomy.service import TaxonomyService
from office365.sharepoint.taxonomy.set import TermSet
from office365.sharepoint.taxonomy.group import TermGroup
from office365.sharepoint.taxonomy.store import TermStore
from office365.sharepoint.taxonomy.term import Term
from tests import test_team_site_url, test_client_credentials
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSPTaxonomy(SPTestCase):
    target_field = None  # type: Field
    tax_svc = None  # type: TaxonomyService
    target_term_group = None  # type: TermGroup
    target_term_set = None  # type: TermSet

    @classmethod
    def setUpClass(cls):
        super(TestSPTaxonomy, cls).setUpClass()
        team_ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
        cls.tax_svc = TaxonomyService(team_ctx)

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_term_store(self):
        term_store = self.tax_svc.term_store.get().execute_query()
        self.assertIsInstance(term_store, TermStore)
        self.assertIsNotNone(term_store.name)

    def test2_get_term_groups(self):
        term_group = self.tax_svc.term_store.term_groups.get_by_name('Geography').get().execute_query()
        self.assertIsNotNone(term_group.resource_path)
        self.assertIsInstance(term_group, TermGroup)
        self.__class__.target_term_group = term_group

    def test3_get_term_sets(self):
        term_sets = self.__class__.target_term_group.term_sets.get().execute_query()
        self.assertGreater(len(term_sets), 0)
        self.assertIsInstance(term_sets[0], TermSet)
        self.__class__.target_term_set = term_sets[0]

    def test4_get_terms(self):
        terms = self.__class__.target_term_set.terms.get().execute_query()
        self.assertGreater(len(terms), 0)
        self.assertIsInstance(terms[0], Term)

    #def test5_search_term(self):
    #    result = self.tax_svc.term_store.search_term("Finland", self.__class__.target_term_set.properties.get('id'))
    #    result = self.tax_svc.term_store.search_term("Finland").execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test6_create_list_tax_field(self):
        ssp_id = "f02be691-d551-462f-aaae-e1c89168cd0b"
        term_set_id = "b49f64b3-4722-4336-9a5c-56c326b344d4"
        tax_field = self.client.web.default_document_library().fields \
            .create_taxonomy_field(name="Category", ssp_id=ssp_id, term_set_id=term_set_id).execute_query()
        self.assertIsNotNone(tax_field.resource_path)
        self.__class__.target_field = tax_field

    def test7_get_tax_field(self):
        existing_field = self.__class__.target_field.get().execute_query()
        self.assertTrue(existing_field.type_as_string, 'TaxonomyFieldType')
        self.assertIsInstance(existing_field, TaxonomyField)
        self.assertIsNotNone(existing_field.text_field_id)
        self.assertIsNotNone(existing_field.lookup_list)
        self.assertIsNotNone(existing_field.lookup_web_id)

        text_field = existing_field.text_field.get().execute_query()
        self.assertIsNotNone(text_field.internal_name)

    def test8_delete_tax_field(self):
        self.__class__.target_field.delete_object().execute_query()
