import uuid
from unittest import TestCase

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password


class TestContentType(TestCase):
    target_ct = None  # type: ContentType

    @classmethod
    def setUpClass(cls):
        super(TestContentType, cls).setUpClass()
        cls.client = GraphClient(acquire_token_by_username_password)

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_compatible_hub_content_types(self):
        cts = (
            self.client.sites.root.content_types.get_compatible_hub_content_types().execute_query()
        )
        self.assertIsNotNone(cts.resource_path)

    def test2_create_site_content_type(self):
        name = "docSet" + uuid.uuid4().hex
        ct = self.client.sites.root.content_types.add(
            name, "0x0120D520"
        ).execute_query()
        self.assertIsNotNone(ct.resource_path)
        self.__class__.target_ct = ct

    # def test3_publish_and_verify_if_published(self):
    #    result = self.__class__.target_ct.publish().is_published().execute_query()
    #    self.assertTrue(result.value)

    # def test4_unpublish(self):
    #    result = self.__class__.target_ct.unpublish().is_published().execute_query()
    #    self.assertFalse(result.value)

    def test5_delete(self):
        ct_to_del = self.__class__.target_ct
        ct_to_del.delete_object().execute_query()
