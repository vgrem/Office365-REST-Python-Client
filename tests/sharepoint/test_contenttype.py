from random import randint

from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.contenttypes.content_type import ContentType
from office365.sharepoint.contenttypes.content_type_collection import ContentTypeCollection
from office365.sharepoint.contenttypes.contentTypeCreationInformation import ContentTypeCreationInformation


class TestContentType(SPTestCase):
    target_ct = None  # type: ContentType

    def test_1_list_site_content_types(self):
        web_cts = self.client.site.rootWeb.contentTypes.get().execute_query()
        self.assertIsInstance(web_cts, ContentTypeCollection)

    def test_2_get_content_type_by_id(self):
        ct = self.client.site.rootWeb.contentTypes.get_by_id("0x0101").get().execute_query()
        self.assertIsNotNone(ct.name)

    def test_3_create_content_type(self):
        cti = ContentTypeCreationInformation("Contoso Document" + str(randint(0, 1000)))
        ct = self.client.site.rootWeb.contentTypes.add(cti).execute_query()
        self.assertIsNotNone(ct.name)
        self.__class__.target_ct = ct

    def test_5_delete_content_type(self):
        web_cts = self.client.site.rootWeb.contentTypes.get().execute_query()
        before_count = len(web_cts)
        self.__class__.target_ct.delete_object().execute_query()
        web_cts = self.client.site.rootWeb.contentTypes.get().execute_query()
        self.assertTrue(before_count, len(web_cts) + 1)

    def test_6_get_content_types_changes(self):
        changes = self.client.web.get_changes(ChangeQuery(content_type=True)).execute_query()
        self.assertGreater(len(changes), 0)
