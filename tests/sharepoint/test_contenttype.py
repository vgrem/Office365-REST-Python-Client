from random import randint

from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.contenttypes.content_type import ContentType
from office365.sharepoint.contenttypes.collection import ContentTypeCollection
from office365.sharepoint.contenttypes.creation_information import ContentTypeCreationInformation


class TestContentType(SPTestCase):
    target_ct = None  # type: ContentType
    localized_title = "Contoso Dokumentti"

    def test1_list_site_content_types(self):
        web_cts = self.client.site.root_web.content_types.get().execute_query()
        self.assertIsInstance(web_cts, ContentTypeCollection)

    def test2_get_content_type_by_id(self):
        ct = self.client.site.root_web.content_types.get_by_id("0x0101").get().execute_query()
        self.assertIsNotNone(ct.name)

    def test3_create_content_type(self):
        cti = ContentTypeCreationInformation("Contoso Document" + str(randint(0, 1000)))
        ct = self.client.site.root_web.content_types.add(cti).execute_query()
        self.assertIsNotNone(ct.name)
        self.__class__.target_ct = ct

    def test4_update_content_type(self):
        ct_to_update = self.__class__.target_ct
        ct_to_update.description = "New desc"
        ct_to_update.update(True).execute_query()
        self.assertIsNotNone(ct_to_update.description)

    def test5_set_value_for_ui_culture(self):
        ct = self.__class__.target_ct
        result = ct.name_resource.set_value_for_ui_culture("fi-FI", self.localized_title).execute_query()
        self.assertIsNotNone(result.value)

    def test6_get_value_for_ui_culture(self):
        ct = self.__class__.target_ct
        result = ct.name_resource.get_value_for_ui_culture("fi-FI").execute_query()
        self.assertIsNotNone(result.value)
        # self.assertEqual(result.value, self.localized_title)

    def test8_delete_content_type(self):
        web_cts = self.client.site.root_web.content_types.get().execute_query()
        before_count = len(web_cts)
        self.__class__.target_ct.delete_object().execute_query()
        web_cts = self.client.site.root_web.content_types.get().execute_query()
        self.assertTrue(before_count, len(web_cts) + 1)

    def test9_get_content_types_changes(self):
        changes = self.client.web.get_changes(ChangeQuery(content_type=True)).execute_query()
        self.assertGreater(len(changes), 0)
