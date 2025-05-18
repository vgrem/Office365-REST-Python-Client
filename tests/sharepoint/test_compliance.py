from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from tests.sharepoint.sharepoint_case import SPTestCase


class TestCompliance(SPTestCase):

    target_list = None  # type: List
    list_item = None  # type: ListItem

    @classmethod
    def setUpClass(cls):
        super(TestCompliance, cls).setUpClass()
        cls.target_list = cls.client.web.lists.get_by_title("Docs")
        # items = lib.items.filter("FSObjType eq 0").get().top(1).execute_query()
        # cls.list_item = items[0]

    def test1_get_site_available_tags(self):
        result = self.client.site.get_available_tags().execute_query()
        self.assertIsNotNone(result.value)

    # def test_2_set_list_compliance_tag(self):
    #    result = self.target_list.set_compliance_tag(
    #        "Legal Record - 5 Years", True, True, True
    #    ).execute_query()
    #    self.assertIsNotNone(result.value)

    def test_3_get_list_compliance_tag(self):
        result = self.target_list.get_compliance_tag().execute_query()
        self.assertIsNotNone(result.value)

    # def test_4_reset_list_compliance_tag(self):
    #    result = self.target_list.set_compliance_tag(
    #        "", False, False, False
    #    ).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_5_enable_place_record_management(self):
    #    result = self.client.site.features.add(
    #        KnownFeaturesList.PlaceRecordsManagement, False, FeatureDefinitionScope.Site
    #    ).execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test_6_lock_record_item(self):
    #    result = self.list_item.lock_record_item().execute_query()
    #    self.assertIsNotNone(result.resource_path)
