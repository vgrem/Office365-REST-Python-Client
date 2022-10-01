import uuid

from office365.onedrive.contenttypes.content_type import ContentType
from tests.graph_case import GraphTestCase


class TestContentType(GraphTestCase):
    target_ct = None  # type: ContentType

    @classmethod
    def setUpClass(cls):
        super(TestContentType, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_compatible_hub_content_types(self):
        cts = self.client.sites.root.content_types.get_compatible_hub_content_types().execute_query()
        self.assertIsNotNone(cts.resource_path)

    def test2_create_site_content_type(self):
        name = "docSet" + uuid.uuid4().hex
        ct = self.client.sites.root.content_types.add(name, "0x0120D520").execute_query()
        self.assertIsNotNone(ct.resource_path)
        self.__class__.target_ct = ct

    def test3_delete(self):
        ct_to_del = self.__class__.target_ct
        ct_to_del.delete_object().execute_query()
