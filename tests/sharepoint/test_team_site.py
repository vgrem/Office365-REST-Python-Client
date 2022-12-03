import uuid
from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.sites.status import SiteStatus
from office365.sharepoint.sites.site import Site
from tests import test_site_url, test_user_credentials


class TestTeamSite(TestCase):
    target_site = None  # type: Site

    @classmethod
    def setUpClass(cls):
        super(TestTeamSite, cls).setUpClass()
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        cls.client = client

    def test1_can_user_create_group(self):
        result = self.client.group_site_manager.can_user_create_group().execute_query()
        self.assertIsNotNone(result.value)

    def test2_create_site(self):
        site_name = "TeamSite{0}".format(uuid.uuid4().hex)
        site = self.client.create_team_site(site_name, "Team Site", True).execute_query()
        self.assertIsNotNone(site.url)
        self.__class__.target_site = site

    def test3_get_site_status(self):
        site = self.__class__.target_site.get().select(["GroupId"]).execute_query()
        result = self.client.group_site_manager.get_status(site.group_id).execute_query()
        self.assertIsNotNone(result.value.SiteStatus)
        self.assertTrue(result.value.SiteStatus == SiteStatus.Ready)

    def test4_get_notebook_url(self):
        group_id = self.__class__.target_site.group_id
        result = self.client.group_site_manager.notebook(group_id).execute_query()
        self.assertIsNotNone(result.value)

    def test5_delete_site(self):
        self.__class__.target_site.delete_object().execute_query()

    def test6_get_current_user_joined_teams(self):
        result = self.client.group_site_manager.get_current_user_joined_teams().execute_query()
        self.assertIsNotNone(result.value)

    def test7_get_group_creation_context(self):
        result = self.client.group_site_manager.get_group_creation_context().execute_query()
        self.assertIsNotNone(result.value)

    def test8_get_current_user_shared_channel_member_groups(self):
        result = self.client.group_site_manager.get_current_user_shared_channel_member_groups().execute_query()
        self.assertIsNotNone(result.value)
