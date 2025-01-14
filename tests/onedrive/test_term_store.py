import uuid

from office365.graph_client import GraphClient
from office365.onedrive.termstore.groups.group import Group
from office365.onedrive.termstore.sets.set import Set
from office365.onedrive.termstore.store import Store
from office365.onedrive.termstore.terms.term import Term
from tests import test_client_id, test_client_secret, test_root_site_url, test_tenant
from tests.graph_case import GraphTestCase


class TestTermStore(GraphTestCase):
    target_store = None  # type: Store
    target_group = None  # type: Group
    target_set = None  # type: Set
    target_term = None  # type: Term

    @classmethod
    def setUpClass(cls):
        super(TestTermStore, cls).setUpClass()
        client = GraphClient(tenant=test_tenant).with_client_secret(
            test_client_id, test_client_secret
        )
        cls.target_store = client.sites.get_by_url(test_root_site_url).term_store

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_groups(self):
        groups = self.target_store.groups.top(1).get().execute_query()
        self.assertLessEqual(len(groups), 1)
        for group in groups:
            self.assertIsNotNone(group.resource_path)

    def test2_create_group(self):
        group_name = "Group_" + uuid.uuid4().hex
        new_group = self.target_store.groups.add(group_name).execute_query()
        self.assertIsNotNone(new_group.resource_path)
        self.__class__.target_group = new_group

    def test3_get_group_by_name(self):
        name = self.__class__.target_group.display_name
        group = self.target_store.groups.get_by_name(name).get().execute_query()
        self.assertIsNotNone(group.resource_path)

    def test4_create_set(self):
        set_name = "Set_" + uuid.uuid4().hex
        new_set = self.target_group.sets.add(set_name).execute_query()
        self.assertIsNotNone(new_set.resource_path)
        self.__class__.target_set = new_set

    def test5_list_sets(self):
        sets = self.target_group.sets.get().execute_query()
        self.assertIsNotNone(sets.resource_path)
        self.assertGreaterEqual(1, len(sets))

    def test6_create_term(self):
        label_name = "Term_" + uuid.uuid4().hex
        new_term = self.target_set.children.add(label_name).execute_query()
        self.assertIsNotNone(new_term.resource_path)
        self.__class__.target_term = new_term

    def test7_list_terms(self):
        terms = self.target_set.terms.get().execute_query()
        self.assertIsNotNone(terms.resource_path)
        self.assertGreaterEqual(1, len(terms))

    def test8_delete_term(self):
        self.target_term.delete_object().execute_query()

    def test9_delete_set(self):
        self.target_set.delete_object().execute_query()

    def test_10_delete_group(self):
        self.target_group.delete_object().execute_query()
