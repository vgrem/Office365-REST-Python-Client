from random import randint
from office365.sharepoint.subwebQuery import SubwebQuery
from tests.sharepoint.sharepoint_case import SPTestCase
from office365.sharepoint.web_creation_information import WebCreationInformation


class TestSharePointWeb(SPTestCase):
    target_web = None
    target_user = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointWeb, cls).setUpClass()

    def test0_get_current_user(self):
        current_user = self.client.web.currentUser
        self.client.load(current_user)
        self.client.execute_query()
        self.assertIsNotNone(current_user.login_name)
        self.__class__.target_user = current_user

    def test1_can_create_web(self):
        target_web_name = "workspace_" + str(randint(0, 100000))
        creation_info = WebCreationInformation()
        creation_info.Url = target_web_name
        creation_info.Title = target_web_name
        self.__class__.target_web = self.client.web.webs.add(creation_info)
        self.client.execute_query()

        results = self.client.web.webs.filter("Title eq '{0}'".format(target_web_name))
        self.client.load(results)
        self.client.execute_query()
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0].resource_path)

    def test2_get_sub_web(self):
        sub_webs = self.client.web.get_sub_webs_filtered_for_current_user(SubwebQuery())
        self.client.execute_query()
        self.assertGreater(len(sub_webs), 0)

    def test3_if_web_updated(self):
        """Test to update Web resource"""
        web_title_updated = self.__class__.target_web.properties["Title"] + "_updated"
        self.__class__.target_web.set_property("Title", web_title_updated)
        self.__class__.target_web.update()
        self.client.execute_query()

        self.client.load(self.__class__.target_web)
        self.client.execute_query()
        self.assertEqual(web_title_updated, self.__class__.target_web.properties['Title'])

    def test4_if_web_deleted(self):
        """Test to delete Web resource"""
        title = self.__class__.target_web.properties['Title']
        self.__class__.target_web.delete_object()
        self.client.execute_query()

        results = self.client.web.webs.filter("Title eq '{0}'".format(title))
        self.client.load(results)
        self.client.execute_query()
        self.assertEqual(len(results), 0)

    def test5_enum_all_webs(self):
        """Test to enumerate all webs within site"""
        result = self.client.web.get_all_webs()
        self.client.execute_query()
        self.assertTrue(len(result.value) > 0)

    def test6_read_list(self):
        site_pages = self.client.web.get_list("SitePages")
        self.client.load(site_pages)
        self.client.execute_query()
        self.assertIsNotNone(site_pages.properties['Title'])

    def test7_get_user_perms(self):
        result = self.client.web.get_user_effective_permissions(self.__class__.target_user.login_name)
        self.client.execute_query()
        self.assertIsNotNone(result.value)
        self.assertGreater(len(result.value.permission_levels), 0)

    def test8_get_user_by_id(self):
        result_user = self.client.web.get_user_by_id(self.__class__.target_user.id)
        self.client.load(result_user)
        self.client.execute_query()
        self.assertEqual(result_user.login_name, self.__class__.target_user.login_name)
